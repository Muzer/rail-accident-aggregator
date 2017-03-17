import raa.input_plugins.tsb
import raa.input_plugins.ntsb
import raa.input_plugins.raib
import raa.input_plugins.raiu
import raa.input_plugins.atsb
import raa.input_plugins.taic
import raa.output_plugins.console_list

accidents = raa.input_plugins.tsb.get_accidents()
accidents += raa.input_plugins.ntsb.get_accidents()
accidents += raa.input_plugins.raib.get_accidents()
accidents += raa.input_plugins.raiu.get_accidents()
accidents += raa.input_plugins.atsb.get_accidents()
accidents += raa.input_plugins.taic.get_accidents()

raa.output_plugins.console_list.output(accidents)
