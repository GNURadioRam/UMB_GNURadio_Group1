"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""
import time
import numpy as np
from gnuradio import gr


class blk(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block
    """Embedded Python Block example - a simple multiply const"""

    def __init__(self):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='Beacon-Based Prediction',   # will show up in GRC
            in_sig=[np.float32, np.float32],
            out_sig=[np.float32]
        )

    def work(self, input_items, output_items):
        """Finds the highest value"""
  
        in0 = input_items[0]
        in1 = input_items[1]
        
        n = min(len(in0), len(in1), len(output_items[0]))

        for i in range(n):
                values = [in0[i], in1[i]]
                output_items[0][i] = np.argmax(values)

        return n

