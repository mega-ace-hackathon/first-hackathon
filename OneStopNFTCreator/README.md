# One Stop NFT Creator


## Problem Statement

Given an image, an asset name ("HackaCoin") and a unit name ("hc"), the competitor should build a python script that generates an ARC-3 (https://github.com/algorandfoundation/ARCs/blob/main/ARCs/arc-0003.md) compliant pure NFT for an address and then transfers it to another (with the corresponding opt-in transaction in between). The only supported metadata fields should be: name, decimals (should be 0 as it is an NFT) and image. The competitor can manually or programatically upload the image and metadata json files to an IPFS service of their choice (e.g. Pinata), taking note of the file’s CID.
When preparing data for the minting transaction, the URL must be of the form _ipfs:://{CID}#arc3_. Make sure the metadata field is computed according to ARC-3 requirements (no extra metadata should be supported for the purpose of this excercise).

Your submission should be a python script named **NFTScript.py**. It should implement a method **mintNFT(algodClient, creatorAddress, creatorPrivateKey, assetName, assetUnitName)** that takes an algod client instance, creator public and private keys, as well as the asset and unit names as inputs, and outputs the created asset's ID. 
It should also implement an ASA transfer script named **transferNFT(algodClient, SenderAddress, SenderPrivateKey, ReceiverAddress, ReceiverPrivateKey, assetID)**, which should receive an algod client instance, sender’s public and private keys, a receiver’s public and private keys, and the previously created asset's ID, and perform a succesful token transfer as its name indicates.


## Tests

For testing purposes, the required asset name and unit name are "HackaCoin" and "hc" respectively.
The testing script will connect to a sandbox and select two accounts (with their public and private addresses). Then it will run both scripts from a competitor, and subsequently test that the token was minted correctly, the transfer took place, and the required metadata fields are ARC-3 compliant.