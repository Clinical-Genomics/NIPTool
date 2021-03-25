from typing import Optional

from NIPTool.server.constants import *


### Batch views:


def get_sample_info(sample):
    """Sample info for sample table in batch view."""

    sample_warnings = get_sample_warnings(sample)

    sample_info_keys = ["Zscore_13", "Zscore_18", "Zscore_21", "CNVSegment", "FF_Formatted", "FFX", "FFY", "Zscore_X"]
    for key in sample_info_keys:
        val = sample.get(key)
        if isinstance(val, (float, int)):
            sample[key] = round(val, 2)
        else:
            sample[key] = ""

    return {
        "sample_id": sample.get("_id"),
        "FF": {"value": sample.get("FF_Formatted"), "warn": sample_warnings.get("FF_Formatted")},
        "CNVSegment": {"value": sample.get("CNVSegment"), "warn": "default", },
        "FFX": {"value": sample.get("FFX"), "warn": "default", },
        "FFY": {"value": sample.get("FFY"), "warn": "default", },
        "Zscore_13": {"value": sample.get("Zscore_13"), "warn": sample_warnings.get("Zscore_13")},
        "Zscore_18": {"value": sample.get("Zscore_18"), "warn": sample_warnings.get("Zscore_18")},
        "Zscore_21": {"value": sample.get("Zscore_21"), "warn": sample_warnings.get("Zscore_21")},
        "Zscore_X": {"value": sample.get("Zscore_X")},
        "Status": _get_status(sample),
        "Include": sample.get("include"),
        "Comment": sample.get("comment", ""),
        "Last_Change": sample.get("change_include_date"),
    }


def _get_status(sample):
    """Get the manually defined sample status for batch table"""

    status_list = []
    for key in TRIS_CHROM_ABNORM + SEX_CHROM_ABNORM:
        status = sample.get(f"status_{key}")
        if status and status != "Normal":
            status_list.append(" ".join([status, key]))
    return ", ".join(status_list)


def _get_ff_warning(fetal_fraction):
    """Get fetal fraction warning based on preset treshold"""
    if fetal_fraction == "":
        return "default"

    if fetal_fraction and fetal_fraction <= FF_TRESHOLD:
        return "danger"
    else:
        return "default"


def get_sample_warnings(sample): #arg pymongo object.. return dict of WarningColorModel
    """"""

    sample_warnings = {}
    fetal_fraction = sample.get('FF_Formatted')
    sample_warnings["FF_Formatted"] = _get_ff_warning(fetal_fraction)
    for key in ["Zscore_13", "Zscore_18", "Zscore_21"]:
        z_score = sample.get(key)
        sample_warnings[key] = _get_tris_warning(z_score, fetal_fraction)

    return sample_warnings


def _get_tris_warning(z_score: float, fetal_fraction: Optional[float])-> str:
    """Get automated trisomi warning, based on preset Zscore thresholds"""

    if fetal_fraction is None or z_score is None:
        return "default"

    if fetal_fraction <= 5:
        smax = TRISOMI_TRESHOLDS["soft_max_ff"]["NCV"]
    else:
        smax = TRISOMI_TRESHOLDS["soft_max"]["NCV"]
    hmin = TRISOMI_TRESHOLDS["hard_min"]["NCV"]
    hmax = TRISOMI_TRESHOLDS["hard_max"]["NCV"]
    smin = TRISOMI_TRESHOLDS["soft_min"]["NCV"]

    if (smax <= z_score < hmax) or (hmin < z_score <= smin):
        warn = "warning"
    elif (z_score >= hmax) or (z_score <= hmin):
        warn = "danger"
    else:
        warn = "default"
    return warn


def get_scatter_data_for_coverage_plot(samples):
    """Coverage Ratio data for Coverage Plot."""

    data = {}
    for sample in samples:
        warnings = get_sample_warnings(sample)
        warnings.pop('FF_Formatted')
        if set(warnings.values()) == {'default'}:
            continue
        sample_id = sample["_id"]
        data[sample_id] = {"x": [], "y": []}
        for chr in range(1, 23):
            ratio = sample.get(f"Chr{str(chr)}_Ratio")
            if ratio is None:
                continue
            data[sample_id]["y"].append(ratio)
            data[sample_id]["x"].append(chr)
    print(data)
    return data


def get_box_data_for_coverage_plot(samples):
    """Coverage Ratio data for Coverage Plot."""
    data = {}
    for chr in range(1, 23):
        data[chr] = []
        for sample in samples:
            ratio = sample.get(f"Chr{str(chr)}_Ratio")
            if ratio is None:
                continue
            data[chr].append(ratio)
    return data


def get_ff_control_normal(adapter):
    """Normal Control Samples for fetal fraction plots"""

    pipe = [
        {
            "$match": {
                "FF_Formatted": {"$ne": "None", "$exists": "True"},
                "FFY": {"$ne": "None", "$exists": "True"},
                "FFX": {"$ne": "None", "$exists": "True"},
                "include": {"$eq": True},
            }
        },
        {
            "$group": {
                "_id": "None",
                "FFY": {"$push": "$FFY"},
                "FFX": {"$push": "$FFX"},
                "FF": {"$push": "$FF_Formatted"},
                "names": {"$push": "$_id"},
                "count": {"$sum": 1},
            }
        },
    ]
    return list(adapter.sample_aggregate(pipe))[0]


def get_ff_control_abnormal(adapter):
    """Abnormal Control Samples for fetal_fraction_XY plot"""
    plot_data = {}
    for abn in SEX_CHROM_ABNORM:
        plot_data[abn] = {}
        pipe = [
            {
                "$match": {
                    f"status_{abn}": {"$ne": "Normal", "$exists": "True"},
                    "include": {"$eq": True},
                }
            },
            {
                "$group": {
                    "_id": {f"status_{abn}": f"$status_{abn}"},
                    "FFX": {"$push": "$FFX"},
                    "FFY": {"$push": "$FFY"},
                    "names": {"$push": "$_id"},
                    "count": {"$sum": 1},
                }
            },
        ]
        for status_dict in adapter.sample_aggregate(pipe):
            status = status_dict["_id"][f"status_{abn}"]
            plot_data[abn][status] = status_dict
    return plot_data


def get_ff_cases(adapter, batch_id):
    """Cases for fetal fraction plot"""

    pipe = [
        {
            "$match": {
                "SampleProject": {"$eq": batch_id},
                "FF_Formatted": {"$ne": "None", "$exists": "True"},
                "FFY": {"$ne": "None", "$exists": "True"},
                "FFX": {"$ne": "None", "$exists": "True"},
                "include": {"$eq": True},
            }
        },
        {
            "$group": {
                "_id": "None",
                "FFY": {"$push": "$FFY"},
                "FFX": {"$push": "$FFX"},
                "FF_Formatted": {"$push": "$FF_Formatted"},
                "names": {"$push": "$_id"},
            }
        },
    ]
    aggregation = list(adapter.sample_aggregate(pipe))

    massaged_data = {}
    if not aggregation:
        return massaged_data
    data = aggregation[0]
    for i, sample_id in enumerate(data["names"]):
        massaged_data[sample_id] = {
            "FFY": data["FFY"][i],
            "FFX": data["FFX"][i],
            "FF": data["FF_Formatted"][i],
        }
    return massaged_data


def get_tris_control_normal(adapter, chr):
    """Normal Control Samples for trisomi plots"""

    pipe = [
        {"$match": {f"status_T{chr}": {"$eq": "Normal"}, "include": {"$eq": True}}},
        {
            "$group": {
                "_id": {f"status_T{chr}": f"$status_T{chr}"},
                "values": {"$push": f"$Zscore_{chr}"},
                "names": {"$push": "$_id"},
                "count": {"$sum": 1},
            }
        },
    ]
    if not list(adapter.sample_aggregate(pipe)):
        return {}
    data = list(adapter.sample_aggregate(pipe))[0]
    data["values"] = [value for value in data.get("values", [])]
    return data


def get_tris_control_abnormal(adapter, chr, x_axis):
    """Abnormal Control Samples for trisomi plots"""

    plot_data = {}

    pipe = [
        {
            "$match": {
                f"status_T{chr}": {"$ne": "Normal", "$exists": "True"},
                "include": {"$eq": True},
            }
        },
        {
            "$group": {
                "_id": {f"status_T{chr}": f"$status_T{chr}"},
                "values": {"$push": f"$Zscore_{chr}"},
                "names": {"$push": "$_id"},
                "count": {"$sum": 1},
            }
        },
    ]

    for status_dict in adapter.sample_aggregate(pipe):
        status = status_dict["_id"][f"status_T{chr}"]
        plot_data[status] = {
            "values": [value for value in status_dict.get("values")],
            "names": status_dict.get("names"),
            "count": status_dict.get("count"),
            "x_axis": [x_axis] * status_dict.get("count"),
        }
    return plot_data


def get_tris_cases(adapter, chr, batch_id):
    """Cases for trisomi plots."""

    pipe = [
        {"$match": {"SampleProject": {"$eq": batch_id}, "include": {"$eq": True}}},
        {
            "$group": {
                "_id": {"batch": "$SampleProject"},
                "values": {"$push": f"$Zscore_{chr}"},
                "names": {"$push": "$_id"},
                "count": {"$sum": 1},
            }
        },
    ]

    if not list(adapter.sample_aggregate(pipe)):
        return {}

    data = list(adapter.sample_aggregate(pipe))[0]
    data["values"] = [value for value in data.get("values")]
    data["x_axis"] = list(range(1, data.get("count") + 1))
    return data


### Sample Trisomi Plot:


def get_abn_for_samp_tris_plot(adapter):
    """Format abnormal Control Samples for Sample trisomi plot"""

    plot_data = {}
    data_per_abnormaliy = {}
    for status in STATUS_CLASSES:
        plot_data[status] = {"values": [], "names": [], "count": 0, "x_axis": []}
    x_axis = 1
    for abn in ["13", "18", "21"]:
        data = get_tris_control_abnormal(adapter, abn, x_axis)
        data_per_abnormaliy[abn] = data

        for status, status_dict in data.items():
            plot_data[status]["values"] += status_dict.get("values", [])
            plot_data[status]["names"] += status_dict.get("names", [])
            plot_data[status]["count"] += status_dict.get("count", 0)
            plot_data[status]["x_axis"] += status_dict.get("x_axis", [])
        x_axis += 1

    return plot_data, data_per_abnormaliy


def get_normal_for_samp_tris_plot(adapter):
    """Format normal Control Samples for Sample trisomi plot"""

    data_per_abnormaliy = {}
    x_axis = 1
    for abn in ["13", "18", "21"]:
        data = get_tris_control_normal(adapter, abn)
        data["x_axis"] = [x_axis] * data.get("count", 0)
        data_per_abnormaliy[abn] = data
        x_axis += 1
    return data_per_abnormaliy


def get_sample_for_samp_tris_plot(sample):
    """Case data for Sample trisomi plot"""

    return {
        "13": {"value": sample.get("Zscore_13"), "x_axis": 1},
        "18": {"value": sample.get("Zscore_18"), "x_axis": 2},
        "21": {"value": sample.get("Zscore_21"), "x_axis": 3},
    }


def get_last_batches(adapter, nr: int) -> list:
    """geting the <nr> last batches based on SequencingDate"""

    batch_sort_aggregation = [{'$sort': {'SequencingDate': -1}}]
    sorted_batches = list(adapter.batch_aggregate(batch_sort_aggregation))
    if len(sorted_batches) > nr:
        sorted_batches = sorted_batches[0:nr]

    return (sorted_batches)


# Statistics

def get_statistics_for_scatter_plot(batches: list, fields: list) -> dict:
    """Formating data for scatter plot"""

    scatter_plot_data = {}
    for batch in batches:
        batch_id = batch.get('_id')
        scatter_plot_data[batch_id] = {
            'date': batch.get('SequencingDate')}
        for field in fields:
            scatter_plot_data[batch_id][field] = batch.get(field)

    return scatter_plot_data


def get_statistics_for_box_plot(adapter, batches: list, fields: list):
    """Getting and formating data for box plot"""

    match = {'$match': {'SampleProject': {'$in': batches}}}
    lookup = {'$lookup': {
        'from': 'batch',
        'localField': 'SampleProject',
        'foreignField': '_id',
        'as': 'batch'}}
    unwind = {'$unwind': {'path': '$batch'}}
    group = {'$group': {'_id': {
        'batch': '$SampleProject',
        'date': '$batch.SequencingDate'}}}

    for field in fields:
        group['$group'][field] = {'$push': f"${field}"}

    pipe = [match, lookup, unwind, group]
    # maybe add a fina sort to the pipe
    box_plot_data = list(adapter.sample_aggregate(pipe))

    return box_plot_data
