import pandas as pd 

def left_circ_rotate(input_value, shift_num): # shift_i: how many bits rotate
    return ((input_value << shift_num) & (2**32 - 1)) | (input_value >> (32 - shift_num)) # & (2**32 - 1): masking under 32bits because, for example, 1101 << 2 -> 110100

def gen_sbox(sbox):
    sbox_df = pd.read_csv('./sbox.csv') # pandas.DataFrame
    sbox_df_list = sbox_df.to_dict(orient='list')
    sbox_val = sbox_df_list['value']
    k = 0
    for i in range(16):
        for j in range(16):
            sbox[k] = int(sbox_val[k], 16)
            k += 1

def gen_fixed_param(fixed_param): 
    for i in range(32):
        ck_ij = [0] * 4
        tmp = '0x'
        for j in range(4):
            ck_ij[j] = ((4 * i + j) * 7) % 256
            tmp += hex(ck_ij[j])[2:].rjust(2, '0')

        fixed_param[i] = int(tmp, 16)

def sbox_operate(sbox_input, sbox):
    tmp = '{:08X}'.format(sbox_input, '0')
    sbox_input = [int(tmp[i:i+2], 16) for i in range(0, len(tmp), 2)]
    sbox_output = [sbox[i] for i in sbox_input]
    tmp = '0x'
    for i in sbox_output:
        tmp += hex(i)[2:].rjust(2, '0')

    return int(tmp, 16)

def permutation_tp(tp_arg, sbox): # k_i: k_param, ck: fixed_param
    # to separate sbox operation

    sbox_output = sbox_operate(tp_arg, sbox)
    return sbox_output ^ (left_circ_rotate(sbox_output, 13)) ^ (left_circ_rotate(sbox_output, 23))

def gen_round_key(round_key, k_param, fixed_param, sbox): # ck: fixed parameter
    k_list = k_param + [0] * 32 # k_list's size needs at least 36
    for i in range(32):
        round_key[i] = k_list[i] ^ permutation_tp(k_list[i+1] ^ k_list[i+2] ^ k_list[i+3] ^ fixed_param[i], sbox)
        k_list[i+4]  = round_key[i]

def permutation_t(t_arg, sbox): 
    sbox_output = sbox_operate(t_arg, sbox)
    return sbox_output ^ (left_circ_rotate(sbox_output, 2)) ^ (left_circ_rotate(sbox_output, 10)) ^ (left_circ_rotate(sbox_output, 18)) ^ (left_circ_rotate(sbox_output, 24))

def encryption(plain_text, sbox, round_key, cipher_text):
    text_list = plain_text + [0] * 32
    for i in range(32):
        text_list[i+4] = text_list[i] ^ permutation_t(text_list[i+1] ^ text_list[i+2] ^ text_list[i+3] ^ round_key[i], sbox)

    for i in range(4):
        cipher_text[i] = text_list[35 - i]

def decryption(cipher_text, sbox, round_key, decrypted_text):
    text_list = cipher_text + [0] * 32
    for i in range(32):
        text_list[i+4] = text_list[i] ^ permutation_t(text_list[i+1] ^ text_list[i+2] ^ text_list[i+3] ^ round_key[31 - i], sbox)

    for i in range(4):
        decrypted_text[i] = text_list[35 - i]

# example plain text and cipher key
plain_text = [0x01234567, 0x89abcdef, 0xfedcba98, 0x76543210]
cipher_key = [0x01234567, 0x89abcdef, 0xfedcba98, 0x76543210]

sys_param = [0xa3b1bac6, 0x56aa3350, 0x677d9197, 0xb27022dc] # fixed
k_param = [cipher_key[i] ^ sys_param[i] for i in range(4)] # initialize by this formula. using to make round key

sbox = [0] * 256
gen_sbox(sbox)

fixed_param = [0] * 32 # fixed_param: using to generate round keys
gen_fixed_param(fixed_param)

round_key = [0] * 32
gen_round_key(round_key, k_param, fixed_param, sbox)

cipher_text = [0] * 4
encryption(plain_text, sbox, round_key, cipher_text)

# decrypted_text = [0] * 4
# decryption(cipher_text, sbox, round_key, decrypted_text)
