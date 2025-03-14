# This script will open the interview transcript, analyse it, assign ICF-Codes to the answers and store them in a separate file.
# The ICF-Codes will be ordinalised. Answers that are negative will be result in -1 , no comment in 0 and positive answers in 1.
# The files can then be used for further analysis, e.g. a Heatmap, comparing the mentioned ICF-Codes to the used wheelchair.
# It uses different packages to recognize similar words and word stems.