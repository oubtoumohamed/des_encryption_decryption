import re

class DESKey():
        
    def __init__(self, k=""):
        # la clé de chiffrement / déchiffrement
        self.key = k
        
        # les sous-clés de 32 bits ( Left / Right )
        self.left_keys = []
        self.right_keys = []

        # les 16 sous-clés finale de 64 bits
        self.keys_16 = []

        self.hexa_to_binary()
        self.generate_keys()
    
    # vérifie si la clé est en binaire ou pas
    def key_is_not_binary(self):
        return len( re.sub( "[0-1 ]", "", self.key) )
    
    # convertir la clé en binaire
    def to_binary( self ):
        if( self.key_is_not_binary() == 0 ):
            return self.key
        
        mp = map(
            bin,
            bytearray( self.key , encoding ='utf-8')
        )
        return ''.join( '' + m.replace('0b', "0" * (10-len(m)) ) for m in mp )
        return [ m.replace('0b', "0" * (10-len(m)) ) for m in mp ]
    
    # convertir la clé de hexadécimale vers binaire
    def hexa_to_binary( self ):
        if( self.key_is_not_binary() == 0 ):
            return self.key
        
        res = "{0:08b}".format(int( self.key , 16))
        
        # dans le cas de message est court on va l'augmenter par des zéros
        if( len(res) < 64 ):
            res = ( "0" * ( 64 - len(res) ) + res )

        self.key =res

    
    # permutation PC-1 pour produire 56 bits
    def permutation_chose_1(self):
        PC1 = [
                57,  49,   41,  33,   25,   17,   9,
                 1,  58,   50,  42,   34,   26,  18,
                10,   2,   59,  51,   43,   35,  27,
                19,  11,    3,  60,   52,   44,  36,
                63,  55,   47,  39,   31,   23,  15,
                 7,  62,   54,  46,   38,   30,  22,
                14,   6,   61,  53,   45,   37,  29,
                21,  13,    5,  28,   20,   12,   4,
            ]
        key_pc1 = ""
        for index in PC1:
            key_pc1 += self.key[index - 1]
        
        return key_pc1

    # diviser le bloc de 56 bits en deux parties de 28 bits
    def split_to_left_right(self, key_pc1):
        self.left_keys.append( key_pc1[:28] )
        self.right_keys.append( key_pc1[28:] )
    
    def left_right_keys(self):
        # generate 16 keys
        for i in range(1, 17):

            # check number of shifts 
            shifts = 2
            if( i in [ 1, 2, 9, 16 ]):
                shifts = 1
            
            self.left_keys.append( 
                self.left_keys[ i-1 ][shifts:]
                 + 
                self.left_keys[ i-1 ][0:shifts]  
            )
            self.right_keys.append( 
                self.right_keys[ i-1 ][shifts:]
                 + 
                self.right_keys[ i-1 ][0:shifts]  
            )
    
    # Fusionner les sous-clés ( left & right ) pour produir les sous-clés finale
    def merge_keys(self):
        for i in range(1, 17):
            self.keys_16.append( self.left_keys[i] + self.right_keys[i] )


    # permutation PC-2
    def permutation_chose_2(self):
        PC2 = [
                14,    17,   11,    24,     1,    5,
                 3,    28,   15,     6,    21,   10,
                23,    19,   12,     4,    26,    8,
                16,     7,   27,    20,    13,    2,
                41,    52,   31,    37,    47,   55,
                30,    40,   51,    45,    33,   48,
                44,    49,   39,    56,    34,   53,
                46,    42,   50,    36,    29,   32,
            ]
        
        for i,key in enumerate( self.keys_16 ) :
            temp = ""
            for index in PC2:
                temp += key[index - 1]
            
            self.keys_16[i] = temp
                    

    def generate_keys(self):
        
        # 1 : permutation chose 1
        key_pc1 = self.permutation_chose_1()

        # 2 : split to left and right
        self.split_to_left_right( key_pc1 )

        # 3 : generate 16 keys left and 16 keys right
        self.left_right_keys()

        # 4 : merge 16 keys each one = left + rigth => variable " keys_16 "
        self.merge_keys()

        # 5 : permutation chose 2
        self.permutation_chose_2()


class DES():
    def __init__(self, txt="", k=""): 
        self.msg = txt         # le message 
        self.key = DESKey( k ) # la clé
        self.result = ""       # le text chiffré 
        
        # la matrice de permutation finale
        self.PF = [            
            40,  8,  48,  16,  56,  24,   64,  32,
            39,  7,  47,  15,  55,  23,   63,  31,
            38,  6,  46,  14,  54,  22,   62,  30,
            37,  5,  45,  13,  53,  21,   61,  29,
            36,  4,  44,  12,  52,  20,   60,  28,
            35,  3,  43,  11,  51,  19,   59,  27,
            34,  2,  42,  10,  50,  18,   58,  26,
            33,  1,  41,   9,  49,  17,   57,  25
        ]
        
        # la matrice de permutation initial
        self.PC = [            
            58,    50,   42,    34,    26,   18,    10,    2,
            60,    52,   44,    36,    28,   20,    12,    4,
            62,    54,   46,    38,    30,   22,    14,    6,
            64,    56,   48,    40,    32,   24,    16,    8,
            57,    49,   41,    33,    25,   17,     9,    1,
            59,    51,   43,    35,    27,   19,    11,    3,
            61,    53,   45,    37,    29,   21,    13,    5,
            63,    55,   47,    39,    31,   23,    15,    7,
        ]

        # les S-box
        self.sbox_elements = [
                [#S1
                    [ 14,  4,  13,  1,   2, 15,  11,  8,   3, 10,   6, 12,   5,  9,   0,  7 ],
                    [  0, 15,   7,  4,  14,  2,  13,  1,  10,  6,  12, 11,   9,  5,   3,  8 ],
                    [  4,  1,  14,  8,  13,  6,   2, 11,  15, 12,   9,  7,   3, 10,   5,  0 ],
                    [ 15, 12,   8,  2,   4,  9,   1,  7,   5, 11,   3, 14,  10,  0,   6, 13 ]
                ],
                [#S2
                    [ 15,  1,   8, 14,   6, 11,   3,  4,   9,  7,   2, 13,  12,  0,   5, 10 ],
                    [  3, 13,   4,  7,  15,  2,   8, 14,  12,  0,   1, 10,   6,  9,  11,  5 ],
                    [  0, 14,   7, 11,  10,  4,  13,  1,   5,  8,  12,  6,   9,  3,   2, 15 ],
                    [ 13,  8,  10,  1,   3, 15,   4,  2,  11,  6,   7, 12,   0,  5,  14,  9 ]
                ],
                [#S3
                    [ 10,  0,   9, 14,   6,  3,  15,  5,   1, 13,  12,  7,  11,  4,   2,  8 ],
                    [ 13,  7,   0,  9,   3,  4,   6, 10,   2,  8,   5, 14,  12, 11,  15,  1 ],
                    [ 13,  6,   4,  9,   8, 15,   3,  0,  11,  1,   2, 12,   5, 10,  14,  7 ],
                    [  1, 10,  13,  0,   6,  9,   8,  7,   4, 15,  14,  3,  11,  5,   2, 12 ]
                ],
                [#S4
                    [  7, 13,  14,  3,   0,  6,   9, 10,   1,  2,   8,  5,  11, 12,   4, 15 ],
                    [ 13,  8,  11,  5,   6, 15,   0,  3,   4,  7,   2, 12,   1, 10,  14,  9 ],
                    [ 10,  6,   9,  0,  12, 11,   7, 13,  15,  1,   3, 14,   5,  2,   8,  4 ],
                    [  3, 15,   0,  6,  10,  1,  13,  8,   9,  4,   5, 11,  12,  7,   2, 14 ]
                ],
                [#S5
                    [  2, 12,   4,  1,   7, 10,  11,  6,   8,  5,   3, 15,  13,  0,  14,  9 ],
                    [ 14, 11,   2, 12,   4,  7,  13,  1,   5,  0,  15, 10,   3,  9,   8,  6 ],
                    [  4,  2,   1, 11,  10, 13,   7,  8,  15,  9,  12,  5,   6,  3,   0, 14 ],
                    [ 11,  8,  12,  7,   1, 14,   2, 13,   6, 15,   0,  9,  10,  4,   5,  3 ]
                ],
                [#S6
                    [ 12,  1,  10, 15,   9,  2,   6,  8,   0, 13,   3,  4,  14,  7,   5, 11 ],
                    [ 10, 15,   4,  2,   7, 12,   9,  5,   6,  1,  13, 14,   0, 11,   3,  8 ],
                    [  9, 14,  15,  5,   2,  8,  12,  3,   7,  0,   4, 10,   1, 13,  11,  6 ],
                    [  4,  3,   2, 12,   9,  5,  15, 10,  11, 14,   1,  7,   6,  0,   8, 13 ]
                ],
                [#S7
                    [  4, 11,   2, 14,  15,  0,   8, 13,   3, 12,   9,  7,   5, 10,   6,  1 ],
                    [ 13,  0,  11,  7,   4,  9,   1, 10,  14,  3,   5, 12,   2, 15,   8,  6 ],
                    [  1,  4,  11, 13,  12,  3,   7, 14,  10, 15,   6,  8,   0,  5,   9,  2 ],
                    [  6, 11,  13,  8,   1,  4,  10,  7,   9,  5,   0, 15,  14,  2,   3, 12 ]
                ],
                [#S8
                    [ 13,  2,   8,  4,   6, 15,  11,  1,  10,  9,   3, 14,   5,  0,  12,  7 ],
                    [  1, 15,  13,  8,  10,  3,   7,  4,  12,  5,   6, 11,   0, 14,   9,  2 ],
                    [  7, 11,   4,  1,   9, 12,  14,  2,   0,  6,  10, 13,  15,  3,   5,  8 ],
                    [  2,  1,  14,  7,   4, 10,   8, 13,  15, 12,   9,  0,   3,  5,   6, 11 ]
                ]
            ]
        #mlk

    # getter de message
    def get_msg(self):
        return self.msg
    
    # vérifie si le message est en binaire ou pas
    def is_binary(self):
        return len( re.sub( "[0-1 ]", "", self.msg) )
    
    # vérifie si le message est en hexadécimal
    def is_hex(self):
        return len( re.sub( "[0-9a-fA-F ]", "", self.msg) )
    
    # convirter le message en hexadécimal => binaire
    def hexa_to_binary(self):
        return "{0:08b}".format(int( self.msg, 16))

    # convirter le binaire en hexadécimal
    def to_hex(self, txt):
        return "{0:0>4X}".format(int(txt, 2))
    
    # convirter le text en binaire
    def text_to_binary( self ):
        self.msg = self.msg.encode('utf-8').hex()
        return self.hexa_to_binary()
    
    # convirter le message en hexadécimal => binaire
    def to_binary( self ):
        if( self.is_binary() == 0 ):
            res = self.get_msg()
        
        if( self.is_hex() == 0 ):
            res = self.hexa_to_binary()
        else:
            res = self.text_to_binary()
        
        # dans le cas de message est court on va l'augmenter par des zéros
        if( len(res) < 64 ):
            res = ( "0" * ( 64 - len(res) ) + res )
        
        return res       
    

    # permutation initial
    def permutation_initial(self):
        txt = self.to_binary()
        res = ""
        for index in self.PC:
            res += txt[index - 1]

        return res
    
    # diviser le bloc de 64 bits en deux parties de 32 bits
    def split_to_32b(self, _64bit):
        return [
            _64bit[:32],
            _64bit[32:]
        ]

    #  étendu Ri-1 de 32 bits à 48 bits, grâce a la table E
    def E(self, Ri):
        E = [
            32,     1,    2,     3,     4,    5,
            4,     5,    6,     7,     8,    9,
            8,     9,   10,    11,    12,   13,
            12,    13,   14,    15,    16,   17,
            16,    17,   18,    19,    20,   21,
            20,    21,   22,    23,    24,   25,
            24,    25,   26,    27,    28,   29,
            28,    29,   30,    31,    32,    1
        ]

        ER = ""
        for index in E:
            ER += Ri[index - 1]

        return ER
    
    # XOR le résultat d E() avec la clé
    def XOR(self, R, K):
        return ''.join( str( int(i != j) ) for i,j in zip(R,K) )
    
    # scindé le bloc de 48 bit en 8 blocs de 6 bits
    def split_48_to_8_blocks(self, f):
        return [ f[i:i+6] for i in range(0,48,6) ]

    # la substitution par des S-box
    def sbox(self, f):
        values = ""

        # split 48 bits, to blocks of six bits.
        blocks = self.split_48_to_8_blocks( f )

        # Each block of six bits will give us an address in a different S box
        for i, block_ in enumerate(blocks):
            row = int( block_[0] + block_[-1], 2) # get row = integer of ( first + last chars from binary block ) 
            col = int( block_[1:-1], 2 ) # get column = integer of ( second + last-1 chars from binary block ) 
            
            # get cel of row & col from Sbox I 
            # and convert it to binary
            val = format( self.sbox_elements[i][row][col], 'b')
            
            # just complete by 0 to giving 4 digits 
            val = "0" * (4 - len(val)) + val
            values += val
        
        return values
 
    # la substitution par des S-box
    def sbox(self, f):
        values = ""
 
        # split 48 bits, to blocks of six bits.
        blocks = self.split_48_to_8_blocks( f )

        # chaque bloc de 6 bits a une valeur dans le S box
        for i, block_ in enumerate(blocks):

            # récupérer la ligne = la première + la dernière caractère
            # du block_ convertir en entier 
            row = int( block_[0] + block_[-1], 2) 

            # récupérer la colonne = les caractères restants
            # du block_ convertir en entier 
            col = int( block_[1:-1], 2 ) 

            # récupérer la valeur correspondant 
            # de la ligne et la colonne a partir de Sbox de i
            # et le convertir en binaire
            val = format( self.sbox_elements[i][row][col], 'b')

            # compléter le val pour avoir 4 chiffres si il est court
            val = "0" * (4 - len(val)) + val

            values += val

        return values
   
    # la fonction f(Ri, Ki)
    def F(self, Ri, K):
        
        # étendu Ri de 32 bits à 48 bits
        ERi = self.E(Ri)
        
        # XOR le résultat d E() avec la clé
        xored = self.XOR( ERi, K )

        # la substitution par des S-box
        sboxed = self.sbox( xored )

        # permutaion P
        permeted = ""
        P = [ 
            16,   7,  20,  21,
            29,  12,  28,  17,
             1,  15,  23,  26,
             5,  18,  31,  10,
             2,   8,  24,  14,
            32,  27,   3,   9,
            19,  13,  30,   6,
            22,  11,   4,  25
        ]

        for indx in P:
            permeted += sboxed[ indx-1 ]

        return permeted
    
    # la permutation finale
    def permutation_finale(self, R16L16):
        return ''.join( R16L16[ i-1 ] for i in self.PF )

    # la fonction main
    def main(self):
        # (I)   Permutaion initial
        res_64bit = self.permutation_initial()

        # (II)  Scindement en blocs de 32 bits
        L0, R0 = self.split_to_32b(res_64bit)

        # (III) Tours
        Ls = []
        Rs = []
        Ls.append( L0 )
        Rs.append( R0 )

        for i in range(1,17):
            Ls.append( Rs[i-1] ) 
            Rs.append( 
                self.XOR( 
                    Ls[i-1],
                    # calcule la fonction f(Ri-1, Ki)
                    self.F( Rs[i-1], self.key.keys_16[i-1] )
                )
            )

        # (V)  Permutation finale
        R16L16 = Rs[16] + Ls[16]
        self.result = self.permutation_finale(R16L16)

    # dans le cas au le message est long on va le divisé par des blocs de 8 bits et les chiffrer
    def chifrrement(self):
        txt = self.msg
        self.msg = ""
        res = ""
        for i in range(0,len(txt),8):
            self.msg = txt[i:i+8]
            self.main()
            res +=  " "+self.to_hex( self.result )
        
        return res
    
    # dans le cas au le message chiffre contient des éspaces c-a-d 
    # qu'il a plusieur mots chiffrer  long on va le diviser
    # par des blocs de 8 bits et les chiffrer
    def dechiffrement(self):
        self.key.keys_16.reverse()

        txt = self.msg.strip().split(' ') 
        self.msg = ""
        res = ""
        for i in txt:
            self.msg = i
            self.main()

            try: 
                tmp = self.to_hex( self.result )
                res += bytes.fromhex(tmp).decode('utf-8')
            except:
                res += res

        return res

msg_ = "Bonjour je suis OUBTOU Mohamed"
key_ = "AE13FD8990EABECD"

des = DES(msg_ , key_)
sh = des.chifrrement()

print("chiffrement : ", sh )

msg_chiffrer = "6E824B2E0261FA70 549D23BDF167B990 EAB4C10B9D3B6278 17C01FBB2F77DCD1"
key_ = "AE13FD8990EABECD"

des = DES(sh, key_)
dsh = des.dechiffrement()

print("le dechiffrement : \n\n", dsh)
