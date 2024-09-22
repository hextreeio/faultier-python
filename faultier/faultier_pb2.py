# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: faultier.proto
# Protobuf Python Version: 5.27.2
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    27,
    2,
    '',
    'faultier.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0e\x66\x61ultier.proto\"\x1f\n\x0f\x43\x61ptureResponse\x12\x0c\n\x04\x64\x61ta\x18\x01 \x01(\x0c\"\x0e\n\x0c\x43ommandHello\"\x10\n\x0e\x43ommandCapture\"\x0f\n\rCommandGlitch\"6\n\x0f\x43ommandSWDCheck\x12#\n\x08\x66unction\x18\x01 \x01(\x0e\x32\x11.SWDCheckFunction\"\xb1\x02\n\x18\x43ommandConfigureGlitcher\x12)\n\x12power_cycle_output\x18\x07 \x01(\x0e\x32\r.GlitchOutput\x12\x1a\n\x12power_cycle_length\x18\x08 \x01(\x05\x12#\n\x0ctrigger_type\x18\x01 \x01(\x0e\x32\r.TriggersType\x12\r\n\x05\x64\x65lay\x18\x02 \x01(\x05\x12\r\n\x05pulse\x18\x03 \x01(\x05\x12&\n\x0etrigger_source\x18\x04 \x01(\x0e\x32\x0e.TriggerSource\x12$\n\rglitch_output\x18\x05 \x01(\x0e\x32\r.GlitchOutput\x12=\n\x1atrigger_pull_configuration\x18\x06 \x01(\x0e\x32\x19.TriggerPullConfiguration\"G\n\x13\x43ommandConfigureADC\x12\x1a\n\x06source\x18\x01 \x01(\x0e\x32\n.ADCSource\x12\x14\n\x0csample_count\x18\x02 \x01(\x05\"\x10\n\x0e\x43ommandReadADC\"\x82\x03\n\x07\x43ommand\x12\x1e\n\x05hello\x18\x01 \x01(\x0b\x32\r.CommandHelloH\x00\x12\x37\n\x12\x63onfigure_glitcher\x18\x02 \x01(\x0b\x32\x19.CommandConfigureGlitcherH\x00\x12-\n\rconfigure_adc\x18\x03 \x01(\x0b\x32\x14.CommandConfigureADCH\x00\x12\"\n\x07\x63\x61pture\x18\x04 \x01(\x0b\x32\x0f.CommandCaptureH\x00\x12 \n\x06glitch\x18\x05 \x01(\x0b\x32\x0e.CommandGlitchH\x00\x12#\n\x08read_adc\x18\x06 \x01(\x0b\x32\x0f.CommandReadADCH\x00\x12%\n\tswd_check\x18\x07 \x01(\x0b\x32\x10.CommandSWDCheckH\x00\x12*\n\x0cio_get_state\x18\x08 \x01(\x0b\x32\x12.CommandIOGetStateH\x00\x12*\n\x0cio_set_state\x18\t \x01(\x0b\x32\x12.CommandIOSetStateH\x00\x42\x05\n\x03\x63md\"\x0c\n\nResponseOk\" \n\rResponseError\x12\x0f\n\x07message\x18\x01 \x01(\t\"2\n\rResponseHello\x12!\n\x07version\x18\x01 \x01(\x0e\x32\x10.FaultierVersion\"\x18\n\x16ResponseTriggerTimeout\"\x1e\n\x0bResponseADC\x12\x0f\n\x07samples\x18\x01 \x01(\x0c\"!\n\x0cResponseInfo\x12\x11\n\tfrequency\x18\x01 \x01(\x05\"#\n\x10ResponseSWDCheck\x12\x0f\n\x07\x65nabled\x18\x01 \x01(\x08\"\x95\x02\n\x08Response\x12\x19\n\x02ok\x18\x01 \x01(\x0b\x32\x0b.ResponseOkH\x00\x12\x1f\n\x05\x65rror\x18\x02 \x01(\x0b\x32\x0e.ResponseErrorH\x00\x12\x1f\n\x05hello\x18\x03 \x01(\x0b\x32\x0e.ResponseHelloH\x00\x12\x1b\n\x03\x61\x64\x63\x18\x04 \x01(\x0b\x32\x0c.ResponseADCH\x00\x12\x32\n\x0ftrigger_timeout\x18\x05 \x01(\x0b\x32\x17.ResponseTriggerTimeoutH\x00\x12&\n\tswd_check\x18\x06 \x01(\x0b\x32\x11.ResponseSWDCheckH\x00\x12+\n\x0cio_get_state\x18\x07 \x01(\x0b\x32\x13.ResponseIOGetStateH\x00\x42\x06\n\x04type\"A\n\x11\x43ommandIOSetState\x12\x13\n\x03pin\x18\x01 \x01(\x0e\x32\x06.IOPin\x12\x17\n\x05state\x18\x02 \x01(\x0e\x32\x08.IOState\"(\n\x11\x43ommandIOGetState\x12\x13\n\x03pin\x18\x01 \x01(\x0e\x32\x06.IOPin\"-\n\x12ResponseIOGetState\x12\x17\n\x05state\x18\x01 \x01(\x0e\x32\x08.IOState*B\n\x0f\x46\x61ultierVersion\x12\x19\n\x15\x46\x41ULTIER_VERSION_ZERO\x10\x00\x12\x14\n\x10\x46\x41ULTIER_VERSION\x10\x01*:\n\x08\x43ommands\x12\r\n\tCMD_RESET\x10\x00\x12\x0e\n\nCMD_GLITCH\x10\x01\x12\x0f\n\x0b\x43MD_CAPTURE\x10\x02*N\n\rTriggerSource\x12\x13\n\x0fTRIGGER_IN_NONE\x10\x00\x12\x13\n\x0fTRIGGER_IN_EXT0\x10\x01\x12\x13\n\x0fTRIGGER_IN_EXT1\x10\x02*s\n\x0cGlitchOutput\x12\x0f\n\x0bOUT_CROWBAR\x10\x00\x12\x0c\n\x08OUT_MUX0\x10\x01\x12\x0c\n\x08OUT_MUX1\x10\x02\x12\x0c\n\x08OUT_MUX2\x10\x03\x12\x0c\n\x08OUT_EXT0\x10\x04\x12\x0c\n\x08OUT_EXT1\x10\x05\x12\x0c\n\x08OUT_NONE\x10\x06*\xae\x01\n\x0cTriggersType\x12\x10\n\x0cTRIGGER_NONE\x10\x00\x12\x10\n\x0cTRIGGER_HIGH\x10\x01\x12\x0f\n\x0bTRIGGER_LOW\x10\x02\x12\x17\n\x13TRIGGER_RISING_EDGE\x10\x03\x12\x18\n\x14TRIGGER_FALLING_EDGE\x10\x04\x12\x1a\n\x16TRIGGER_PULSE_POSITIVE\x10\x05\x12\x1a\n\x16TRIGGER_PULSE_NEGATIVE\x10\x06*k\n\x05IOPin\x12\x08\n\x04PIN0\x10\x00\x12\x08\n\x04PIN1\x10\x01\x12\x08\n\x04PIN2\x10\x02\x12\x08\n\x04PIN3\x10\x03\x12\x08\n\x04PIN4\x10\x04\x12\x08\n\x04PIN5\x10\x05\x12\x08\n\x04PIN6\x10\x06\x12\x08\n\x04PIN7\x10\x07\x12\x08\n\x04PIN8\x10\x08\x12\x08\n\x04PIN9\x10\t*8\n\tADCSource\x12\x0f\n\x0b\x41\x44\x43_CROWBAR\x10\x00\x12\x0c\n\x08\x41\x44\x43_MUX0\x10\x01\x12\x0c\n\x08\x41\x44\x43_EXT1\x10\x02*Q\n\x0b\x41uxFunction\x12\x0c\n\x08\x41UX_NONE\x10\x00\x12\x0c\n\x08\x41UX_UART\x10\x01\x12\x13\n\x0f\x41UX_SWD_CHECKER\x10\x02\x12\x11\n\rAUX_SWD_PROBE\x10\x03*>\n\x10SWDCheckFunction\x12\x15\n\x11SWD_CHECK_ENABLED\x10\x00\x12\x13\n\x0fSWD_CHECK_NRF52\x10\x01*]\n\x18TriggerPullConfiguration\x12\x15\n\x11TRIGGER_PULL_NONE\x10\x00\x12\x13\n\x0fTRIGGER_PULL_UP\x10\x01\x12\x15\n\x11TRIGGER_PULL_DOWN\x10\x02*\x1c\n\x07IOState\x12\x07\n\x03LOW\x10\x00\x12\x08\n\x04HIGH\x10\x01\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'faultier_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_FAULTIERVERSION']._serialized_start=1612
  _globals['_FAULTIERVERSION']._serialized_end=1678
  _globals['_COMMANDS']._serialized_start=1680
  _globals['_COMMANDS']._serialized_end=1738
  _globals['_TRIGGERSOURCE']._serialized_start=1740
  _globals['_TRIGGERSOURCE']._serialized_end=1818
  _globals['_GLITCHOUTPUT']._serialized_start=1820
  _globals['_GLITCHOUTPUT']._serialized_end=1935
  _globals['_TRIGGERSTYPE']._serialized_start=1938
  _globals['_TRIGGERSTYPE']._serialized_end=2112
  _globals['_IOPIN']._serialized_start=2114
  _globals['_IOPIN']._serialized_end=2221
  _globals['_ADCSOURCE']._serialized_start=2223
  _globals['_ADCSOURCE']._serialized_end=2279
  _globals['_AUXFUNCTION']._serialized_start=2281
  _globals['_AUXFUNCTION']._serialized_end=2362
  _globals['_SWDCHECKFUNCTION']._serialized_start=2364
  _globals['_SWDCHECKFUNCTION']._serialized_end=2426
  _globals['_TRIGGERPULLCONFIGURATION']._serialized_start=2428
  _globals['_TRIGGERPULLCONFIGURATION']._serialized_end=2521
  _globals['_IOSTATE']._serialized_start=2523
  _globals['_IOSTATE']._serialized_end=2551
  _globals['_CAPTURERESPONSE']._serialized_start=18
  _globals['_CAPTURERESPONSE']._serialized_end=49
  _globals['_COMMANDHELLO']._serialized_start=51
  _globals['_COMMANDHELLO']._serialized_end=65
  _globals['_COMMANDCAPTURE']._serialized_start=67
  _globals['_COMMANDCAPTURE']._serialized_end=83
  _globals['_COMMANDGLITCH']._serialized_start=85
  _globals['_COMMANDGLITCH']._serialized_end=100
  _globals['_COMMANDSWDCHECK']._serialized_start=102
  _globals['_COMMANDSWDCHECK']._serialized_end=156
  _globals['_COMMANDCONFIGUREGLITCHER']._serialized_start=159
  _globals['_COMMANDCONFIGUREGLITCHER']._serialized_end=464
  _globals['_COMMANDCONFIGUREADC']._serialized_start=466
  _globals['_COMMANDCONFIGUREADC']._serialized_end=537
  _globals['_COMMANDREADADC']._serialized_start=539
  _globals['_COMMANDREADADC']._serialized_end=555
  _globals['_COMMAND']._serialized_start=558
  _globals['_COMMAND']._serialized_end=944
  _globals['_RESPONSEOK']._serialized_start=946
  _globals['_RESPONSEOK']._serialized_end=958
  _globals['_RESPONSEERROR']._serialized_start=960
  _globals['_RESPONSEERROR']._serialized_end=992
  _globals['_RESPONSEHELLO']._serialized_start=994
  _globals['_RESPONSEHELLO']._serialized_end=1044
  _globals['_RESPONSETRIGGERTIMEOUT']._serialized_start=1046
  _globals['_RESPONSETRIGGERTIMEOUT']._serialized_end=1070
  _globals['_RESPONSEADC']._serialized_start=1072
  _globals['_RESPONSEADC']._serialized_end=1102
  _globals['_RESPONSEINFO']._serialized_start=1104
  _globals['_RESPONSEINFO']._serialized_end=1137
  _globals['_RESPONSESWDCHECK']._serialized_start=1139
  _globals['_RESPONSESWDCHECK']._serialized_end=1174
  _globals['_RESPONSE']._serialized_start=1177
  _globals['_RESPONSE']._serialized_end=1454
  _globals['_COMMANDIOSETSTATE']._serialized_start=1456
  _globals['_COMMANDIOSETSTATE']._serialized_end=1521
  _globals['_COMMANDIOGETSTATE']._serialized_start=1523
  _globals['_COMMANDIOGETSTATE']._serialized_end=1563
  _globals['_RESPONSEIOGETSTATE']._serialized_start=1565
  _globals['_RESPONSEIOGETSTATE']._serialized_end=1610
# @@protoc_insertion_point(module_scope)
