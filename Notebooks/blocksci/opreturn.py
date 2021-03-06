import binascii
import re
import Crypto.Cipher.ARC4
from blocksci import *

op_return_services = {"OA":"Open Assets", "id":"Blockstack", 
                      "S1":"Stampery","S2":"Stampery","S3":"Stampery","S4":"Stampery","S5":"Stampery", 
                      "Factom!!":"Factom", "FACTOM00":"Factom", "Fa":"Factom", "FA":"Factom",
                      "ORIGMY":"OriginalMy",
                      "ProveBit":"ProveBit",
                      "UNicDC":"University of Nicosia",
                      "CryptoTests-":"CryptoCopyright", "CryptoProof-":"CryptoCopyright",
                      "DOCPROOF":"Proof of Existence",
                      "omni":"Omni Layer", "ASCRIBESPOOL":"Ascribe", 
                      "CC":"Colu", "MG":"Monegraph", 
                      "SB.D":"SB.D", "BITPROOF":"Bitproof", "KC":"KC", "BS":"BlockSign", "OC":"UnknownOC", 
                      "CryptoTests-":"Crypto Copyright", "CryptoProof-":"Crypto Copyright", 
                      "LaPreuve":"LaPreuve", 
                      "RMBd":"Remembr", "RMBe":"Remembr", 
                      "Mined by 1hash.com":"1hash",
                      "FluxST":"FluxST", "CP110400":"CP1", "KMD":"Komodo", "OKT":"OKT"}
byte_prefixes = {b'g\x01\xdd6\x15&]+':"UnknownBytePrefix", \
                binascii.unhexlify(b'5888'):"Blockstack", binascii.unhexlify(b'5808'):"Blockstack",
                binascii.unhexlify(b'455720'):"Eternity Wall",
                binascii.unhexlify(b'53504b'):"Coinspark",
                binascii.unhexlify(b'4f43'):"Openchain",
                b'STAMPD##':"stampd",
                b'CNTRPRTY':"Counterparty"
                }
exact_string_matches = ["http://www.blockcypher.com/", "http://www.blockcypher.com", "DS", \
                        "503: Bitcoin over capacity!", "XX", "XY", "XW", "SS"]
exact_byte_matches = [
    b'\xb3\x87\xfc~\xf6K3\xcf\x01\x82\xec\xf8\xea\xb2\x065\x8cz\xc7\xb5\xa9\xd1$\x1a\x11\xd4Sb\xda\x9af\xa2\xb9l\xb6\xb6\x9b\xd7\xa6a',
    b"\xe3\xb0\xc4B\x98\xfc\x1c\x14\x9a\xfb\xf4\xc8\x99o\xb9$'\xaeA\xe4d\x9b\x93L\xa4\x95\x99\x1bxR\xb8U",
    b'\xfc\xf4=\xa2D\x99GZ\x96\x00#1\xb8\x97\xc8\xf3#+(\xe5z\xfd\xcb?}y\x91\xbfv\xc8\xf0\xb6\x05\x81\xa2\x89\x9d\x80\x9f\xa9',
    b'*K\x94V\x827C\xfe\xc9\xc0\x7fv:\x9f\x0c\xa3@~\xba\xb2\xfa\xca\xe4\x0e\xbbm\x83\xc8\xf5k\x0b\xbf\x94\xcbn\xe7\xb0\x9a$\r'
]

address_matches = {
    Address(155316552, pubkeyhash):"Chainpoint",
    Address(89427334, pubkeyhash):"Base64DataAddress1",
    Address(156665979, pubkeyhash):"Base64DataAddress2",
    Address(182075165, pubkeyhash):"Base64DataAddress3",
    Address(156599323, pubkeyhash):"Base64DataAddress4",
    Address(203933727, pubkeyhash):"Komodo",
    Address(203831434, pubkey):"Komodo",
    Address(127559021, pubkeyhash): "UnknownAddress1",
    Address(16179390, scripthash):"SpamAddress1",
    Address(16163151, scripthash):"SpamAddress2",
    Address(89403362, pubkeyhash):"SpamAddress3",
    Address(155249896, pubkeyhash):"SpamAddress4",
    Address(77604537, pubkeyhash):"SpamAddress5",
    Address(127504441, pubkeyhash):"SpamAddress5"
}

def label_application(tx):
    if tx.op_return is None:
        return None
    data = tx.op_return.address.script.data
      
    if len(data) == 0:
        return "Empty"
      
    decoded = data.decode("ascii", "replace")
    strings = re.findall("[a-zA-Z0-9.://! ]+", decoded)
      
    if decoded in exact_string_matches:
        return decoded
    elif data in exact_byte_matches:
        return data
    elif len(strings) > 0 and strings[0].startswith(tuple(op_return_services.keys())):
        for prefix in op_return_services:
            if strings[0].startswith(prefix):
                return op_return_services[prefix]
    elif data.startswith(tuple(byte_prefixes.keys())):
      for prefix in byte_prefixes:
          if data.startswith(prefix):
              return byte_prefixes[prefix]
    elif len(set(txout.address for txout in tx.outs).intersection(set(address_matches.keys()))) > 0:
        for txout in tx.outs:
            if txout.address in address_matches:
                return address_matches[txout.address]
    elif len(tx.ins) > 0:
        first_vin_txid = binascii.unhexlify(str(tx.ins[0].spent_tx.hash))
        decoded = Crypto.Cipher.ARC4.new(first_vin_txid).decrypt(data)
        if decoded.startswith(b'CNTRPRTY'):
            return "Counterparty"
    return "Unknown"
