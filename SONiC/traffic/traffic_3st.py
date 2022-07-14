from trex_stl_lib.api import *

class STLS1(object):

    def __init__ (self):
        self.fsize  =64; # the size of the packet 


    def create_stream (self):

        # Create base packet and pad it to size
        size = self.fsize - 4; # HW will add 4 bytes ethernet FCS
        base_pkt =  Ether()/IP(src="10.0.5.2",dst="10.0.6.2")/UDP(dport=12,sport=1025)
        base_pkt1 =  Ether()/IP(src="10.0.5.3",dst="10.0.6.2")/UDP(dport=12,sport=1025)
        base_pkt2 =  Ether()/IP(src="10.0.5.4",dst="10.0.6.2")/UDP(dport=12,sport=1025)
        pad = max(0, size - len(base_pkt)) * 'x'


        return STLProfile( [ STLStream( isg = 1.0, # start in delay in usec 
                                        packet = STLPktBuilder(pkt = base_pkt/pad),
                                        mode = STLTXCont( pps = 10),
                                        ), 

                             STLStream( isg = 2.0,
                                        packet  = STLPktBuilder(pkt = base_pkt1/pad),
                                        mode    = STLTXCont( pps = 20),
                                        ),

                             STLStream(  isg = 3.0,
                                         packet = STLPktBuilder(pkt = base_pkt2/pad),
                                         mode    = STLTXCont( pps = 30)
                                         
                                        )
                            ]).get_streams()


    def get_streams (self, direction = 0, **kwargs):
        # create 1 stream 
        return self.create_stream() 


# dynamic load - used for trex console or emulator
def register():
    return STLS1()




