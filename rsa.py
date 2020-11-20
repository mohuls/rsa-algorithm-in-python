import os
import sys
import random
from termcolor import colored

def gcd(a, b):
    if (b == 0):
        return a
    else:
        return gcd(b, a % b)

def xgcd(a, b):
    x, old_x = 0, 1
    y, old_y = 1, 0

    while (b != 0):
        quotient = a // b
        a, b = b, a - quotient * b
        old_x, x = x, old_x - quotient * x
        old_y, y = y, old_y - quotient * y

    return a, old_x, old_y

def chooseE(totient):
    while (True):
        e = random.randrange(2, totient)

        if (gcd(e, totient) == 1):
            return e

def chooseKeys():
    rand1 = random.randint(100, 300)
    rand2 = random.randint(100, 300)

    fo = open('primes.txt', 'r')
    lines = fo.read().splitlines()
    fo.close()

    p1 = int(lines[rand1])
    p2 = int(lines[rand2])

    n = p1 * p2
    totient = (p1 - 1) * (p2 - 1)
    e = chooseE(totient)

    # compute d, 1 < d < totient such that ed = 1 (mod totient)
    # e and d are inverses (mod totient)
    gcd, x, y = xgcd(e, totient)

    # make sure d is positive
    if (x < 0):
        d = x + totient
    else:
        d = x

    # write the public keys n and e to a file
    f_public = open('public_keys.txt', 'w')
    f_public.write(str(n) + '\n')
    f_public.write(str(e) + '\n')
    f_public.close()

    f_private = open('private_keys.txt', 'w')
    f_private.write(str(n) + '\n')
    f_private.write(str(d) + '\n')
    f_private.close()

def encrypt(message, block_size = 2):
    fo = open('public_keys.txt', 'r')
    n = int(fo.readline())
    e = int(fo.readline())
    fo.close()

    encrypted_blocks = []
    ciphertext = -1

    if (len(message) > 0):
        # initialize ciphertext to the ASCII of the first character of message
        ciphertext = ord(message[0])

    for i in range(1, len(message)):
        # add ciphertext to the list if the max block size is reached
        # reset ciphertext so we can continue adding ASCII codes
        if (i % block_size == 0):
            encrypted_blocks.append(ciphertext)
            ciphertext = 0

        # multiply by 1000 to shift the digits over to the left by 3 places
        # because ASCII codes are a max of 3 digits in decimal
        ciphertext = ciphertext * 1000 + ord(message[i])

    # add the last block to the list
    encrypted_blocks.append(ciphertext)

    # encrypt all of the numbers by taking it to the power of e
    # and modding it by n
    for i in range(len(encrypted_blocks)):
        encrypted_blocks[i] = str((encrypted_blocks[i]**e) % n)

    # create a string from the numbers
    encrypted_message = " ".join(encrypted_blocks)

    return encrypted_message

def decrypt(blocks, block_size = 2):
    """
    Decrypts a string of numbers by raising each number to the power of d and 
    taking the modulus of n. Returns the message as a string.
    block_size refers to how many characters make up one group of numbers in
    each index of blocks.
    """

    fo = open('private_keys.txt', 'r')
    n = int(fo.readline())
    d = int(fo.readline())
    fo.close()

    # turns the string into a list of ints
    list_blocks = blocks.split(' ')
    int_blocks = []

    for s in list_blocks:
        int_blocks.append(int(s))

    message = ""

    # converts each int in the list to block_size number of characters
    # by default, each int represents two characters
    for i in range(len(int_blocks)):
        # decrypt all of the numbers by taking it to the power of d
        # and modding it by n
        int_blocks[i] = (int_blocks[i]**d) % n
        
        tmp = ""
        # take apart each block into its ASCII codes for each character
        # and store it in the message string
        for c in range(block_size):
            tmp = chr(int_blocks[i] % 1000) + tmp
            int_blocks[i] //= 1000
        message += tmp

    return message

def main():
    try:
        open('public_keys.txt', 'r')
    except FileNotFoundError:
        newKeys = input(colored("No keys was found. Do you want to generate one (y, n): ", 'yellow'))
        if (newKeys == 'y'):
            chooseKeys()
        else:
            print(colored("Exiting program...", 'red', attrs=['bold']))
            exit()
    else:
        print(colored("Keys was found!", 'green'))
        print(colored("Warning: Regenerating keys won't work for existing encrypted data.", 'red', attrs=['reverse']))
        again = input("Do you want to regenarate again (y, n): ")
        if again == 'y':
            chooseKeys()       
            os.remove('encrypted.txt')
    choice = input('Encrypt or decrypt? (Enter e or d): ')
    if (choice == 'e'):
        message = input(colored('Enter a text to encrypt: ', 'green'))
        print(colored('Encrypting...', 'cyan', attrs=['bold']))
        print(encrypt(message))
        try:
            open('encrypted.txt', 'r')
        except FileNotFoundError:
            encrypted = open('encrypted.txt', 'w')
            encrypted.write(encrypt(message) + "\n")
        else:
            encrypted = open('encrypted.txt', 'a')
            encrypted.write(encrypt(message) + "\n")
    elif (choice == 'd'):
        try:
            open('encrypted.txt', 'r')
        except FileNotFoundError:
            print(colored("No Encrypted data found!", 'red', attrs=['bold']))
            print("Exiting...")
            exit()
        else:
            encrypted = open('encrypted.txt', 'r')
            print(colored("List of encrypted ciphertext...", 'green'))
            print(colored('----------------------------------------', 'green'))
            print(colored(encrypted.read(), 'magenta'))
            print(colored('----------------------------------------', 'green'))
            encrypted.close()
        message = input('Enter ciphertext to decrypt: ')
        print(colored('Decrypting...', 'red', attrs=['bold']))
        print(decrypt(message))
    else:
        print('Invalid choice!')

if __name__ == "__main__": 
    main()