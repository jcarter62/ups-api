import os


class Site:
    def __init__(self, host, desc1_oid, desc2_oid, temp_oid):
        self.host = host
        self.desc1_oid = desc1_oid
        self.desc2_oid = desc2_oid
        self.description1 = ''
        self.description2 = ''
        self.temperature_f_oid = temp_oid
        self.temperature_f = 0


    def __load_data__(self):
        self.description1 = self.__get_snmp_data__(self.desc1_oid)
        self.description2 = self.__get_snmp_data__(self.desc2_oid)
        self.temperature_f = self.__get_snmp_data__(self.temperature_f_oid)


    def __get_snmp_data__(self, oid):
        cmdexe = os.getenv('SNMPGET', 'snmpget')
        cmd = cmdexe + ' -r:' + self.host + ' -q -v:1 -c:public -o:' + oid
        data = os.popen(cmd).read().strip()
        return data

