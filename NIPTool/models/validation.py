requiered_fields = ["SampleID"]

strings = [
    "SampleID",
    "SampleType",
    "SequencingDate",
    "Flowcell",
    "SampleProject",
    "Index1",
    "Index2",
    "CNVSegment"
]

exceptions = ["nan", None, [], ""]

ints = [
    "Chr1",
    "Chr2",
    "Chr3",
    "Chr4",
    "Chr5",
    "Chr6",
    "Chr7",
    "Chr8",
    "Chr9",
    "Chr10",
    "Chr11",
    "Chr12",
    "Chr13",
    "Chr14",
    "Chr15",
    "Chr16",
    "Chr17",
    "Chr18",
    "Chr19",
    "Chr20",
    "Chr21",
    "Chr22",
    "ChrX",
    "ChrY",
    "MappedReads",
    "UnfilteredCNVcalls",
]

floats = [
    "Library_nM",
    "Zscore_13",
    "Zscore_18",
    "Zscore_21",
    "Zscore_X",
    "Chr13_Ratio",
    "Chr18_Ratio",
    "Chr21_Ratio",
    "ChrX_Ratio",
    "Chr1_Ratio",
    "Chr2_Ratio",
    "Chr3_Ratio",
    "Chr4_Ratio",
    "Chr5_Ratio",
    "Chr6_Ratio",
    "Chr7_Ratio",
    "Chr8_Ratio",
    "Chr9_Ratio",
    "Chr10_Ratio",
    "Chr11_Ratio",
    "Chr12_Ratio",
    "Chr14_Ratio",
    "Chr15_Ratio",
    "Chr16_Ratio",
    "Chr17_Ratio",
    "Chr19_Ratio",
    "Chr20_Ratio",
    "Chr22_Ratio",
    "ChrY_Ratio",
    "Median_13",
    "Median_18",
    "Median_21",
    "Median_X",
    "Median_Y",
    "Stdev_13",
    "Stdev_18",
    "Stdev_21",
    "Stdev_X",
    "Stdev_Y",
    "FF_Formatted",
    "FFY",
    "FFX",
    "DuplicationRate",
    "GC_Dropout",
    "AT_Dropout",
    "Bin2BinVariance",

]
req_str = {'type': 'string', 'required': True}
nreq_str = {'type': 'string', 'required': False}

batch_load_schema = {'concentrations': nreq_str,
                     'project_name': req_str,
                     'result_file': req_str,
                     'multiqc_report': nreq_str,
                     'segmental_calls': nreq_str}

user_load_schema = {'email': req_str, 'name': req_str, 'role': req_str}
