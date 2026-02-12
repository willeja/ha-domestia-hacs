# Domestia protocol constants

# Commands
CMD_ATMAC = [255,0,0,1,0x8A]
CMD_ATRSTYPE = [255,0,0,1,66]
CMD_ATTEMP = [255,0,0,1,29]
CMD_ATRTEMPSTATUS = [255,0,0,1,59]
CMD_ATRRELAIS = [255,0,0,1,156]

# Name requests
ATRNOMS = 62     # Output name
ATRNOMC = 80     # Cover name (voor later)

def build_crc(values):
    """Compute Domestia CRC."""
    return sum(values[4:]) % 256


__all__ = [
    "CMD_ATMAC",
    "CMD_ATRSTYPE",
    "CMD_ATTEMP",
    "CMD_ATRTEMPSTATUS",
    "CMD_ATRRELAIS",
    "ATRNOMS",
    "ATRNOMC",
    "build_crc",
]