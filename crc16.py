# Wieviele Bytes sollen uebertragen werden
# SC_Amount = 6
# Zu uebertragende Bytes
# SC_Buffer = bytearray([0x01, 0x01, 0x00, 0x10, 0x00, 0x10])

def getCRC16(SC_Buffer):
	SC_Amount = len(SC_Buffer)
	SC_Buffer = bytearray(SC_Buffer)
	# initialisation
	Crc = 0xFFFF
	m = SC_Amount
	x = 0

	# loop over all bits
	while(m > 0):

	    Crc ^= SC_Buffer[x]
	    for n in range(8):
	        if(Crc & 1):
	            Crc >>= 1
	            Crc ^= 0xA001
	        else:
	            Crc >>= 1
	    m -= 1
	    x += 1

	# result
	CRC_H = (Crc >> 8) & 0xFF
	CRC_L = Crc & 0xFF

	#print CRC_L, CRC_H
	#print hex(CRC_L), hex(CRC_H)

	return CRC_L, CRC_H


# getCRC16([0x01, 0x01, 0x00, 0x10, 0x00, 0x10])
