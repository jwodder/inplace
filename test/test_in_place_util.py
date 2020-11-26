def pylistdir(d):
    return sorted(p.basename for p in d.listdir())

TEXT = (
    "'Twas brillig, and the slithy toves\n"
    "\tDid gyre and gimble in the wabe;\n"
    "All mimsy were the borogoves,\n"
    "\tAnd the mome raths outgrabe.\n"
    '\n'
    '"Beware the Jabberwock, my son!\n'
    '\tThe jaws that bite, the claws that catch!\n'
    'Beware the Jubjub bird, and shun\n'
    '\tThe frumious Bandersnatch!"\n'
    '\n'
    'He took his vorpal sword in hand:\n'
    '\tLong time the manxome foe he sought--\n'
    'So rested he by the Tumtum tree,\n'
    '\tAnd stood awhile in thought.\n'
    '\n'
    'And as in uffish thought he stood,\n'
    '\tThe Jabberwock, with eyes of flame,\n'
    'Came whiffling through the tulgey wood,\n'
    '\tAnd burbled as it came!\n'
    '\n'
    'One, two!  One, two!  And through and through\n'
    '\tThe vorpal blade went snicker-snack!\n'
    'He left it dead, and with its head\n'
    '\tHe went galumphing back.\n'
    '\n'
    '"And hast thou slain the Jabberwock?\n'
    '\tCome to my arms, my beamish boy!\n'
    'O frabjous day!  Callooh!  Callay!"\n'
    '\tHe chortled in his joy.\n'
    '\n'
    "'Twas brillig, and the slithy toves\n"
    "\tDid gyre and gimble in the wabe;\n"
    "All mimsy were the borogoves,\n"
    "\tAnd the mome raths outgrabe.\n"
)

UNICODE = 'åéîøü\n'
