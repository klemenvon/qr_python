from qrgen.reedsolomon import RSBlock

config = (20, 45, 15, 61, 46, 16)
block_config = [config[i:i + 3] for i in range(0, len(config), 3)]

blocks = [
    RSBlock(total_words=total, data_words=data)
    for count, total, data in block_config
    for _ in range(count)
]
## WOW this really got list comprehension to click!
# idk why I didn't try writing it out line by line like this

print(config)
print(block_config)
print(blocks)
print(len(blocks))