
import os


base_path = os.getcwd()[:-7]
if base_path[-1] != '/':
    base_path += '/'

os.makedirs(base_path + 'data/ABI/GOES-16/L2-CMIPF/temp', exist_ok=True)
os.makedirs(base_path + 'data/ABI/GOES-16/L2-CMIPM/temp', exist_ok=True)
os.makedirs(base_path + 'data/additional_data/colorpalettes', exist_ok=True)
os.makedirs(base_path + 'images/GOES-16/single_band', exist_ok=True)
os.makedirs(base_path + 'images/GOES-16/band_difference', exist_ok=True)
os.makedirs(base_path + 'images/GOES-16/ndvi', exist_ok=True)
os.makedirs(base_path + 'images/GOES-16/composite', exist_ok=True)
os.makedirs(base_path + 'images/GOES-16/ssim', exist_ok=True)

os.rename(base_path + 'scripts/' + 'rainbowIRsummer.txt',
          base_path + 'data/additional_data/colorpalettes/' + 'rainbowIRsummer.txt')

print('created all folders')
print('moved IR-Classic colormap to data/additional_data/colorpalettes/')
print('write the following path into the beginning of the scripts:')
print(base_path)
