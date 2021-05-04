from typing import List, Dict

from NIPTool.API.external.api.models import (
    SampleWarning,
    CoveragePlotSampleData,
    FetalFraction,
    FetalFractionControlAbNormal,
    FetalFractionStatus,
    Sample,
)
from NIPTool.adapter import NiptAdapter
from NIPTool.crud import find
from NIPTool.models.database import DataBaseSample
from NIPTool.API.external.constants import *


### Batch views:

#    for key in sample_info_keys:
#        val = sample.get(key)
#        if isinstance(val, (float, int)):
#            sample[key] = round(val, 2)
#        else:
#            sample[key] = ""


def get_sample_info(sample: DataBaseSample) -> DataBaseSample:
    """Sample info for sample table in batch view."""

    samp = Sample(**sample.dict())
    sample_warnings: SampleWarning = get_sample_warnings(sample=sample)

    samp.warnings = sample_warnings

    return samp


def _get_ff_warning(fetal_fraction: float) -> str:
    """Get fetal fraction warning based on preset threshold"""

    if isinstance(fetal_fraction, float) and fetal_fraction <= FF_TRESHOLD:
        return "danger"

    return "default"


def get_sample_warnings(sample: DataBaseSample) -> SampleWarning:
    """"""

    sample = sample.dict()
    sample_warnings = {}
    fetal_fraction = sample.get("FF_Formatted")
    sample_warnings["FF_Formatted"]: str = _get_ff_warning(fetal_fraction=fetal_fraction)
    for key in ["Zscore_13", "Zscore_18", "Zscore_21"]:
        z_score = sample.get(key)
        sample_warnings[key]: str = _get_tris_warning(
            z_score=z_score, fetal_fraction=fetal_fraction
        )

    return SampleWarning(**sample_warnings)


def _get_tris_warning(z_score: float, fetal_fraction: float) -> str:
    """Get automated trisomy warning, based on preset Zscore thresholds"""

    if fetal_fraction is None or z_score is None:
        return "default"

    if fetal_fraction <= 5:
        soft_max = TRISOMI_TRESHOLDS["soft_max_ff"]["NCV"]
    else:
        soft_max = TRISOMI_TRESHOLDS["soft_max"]["NCV"]
    hard_min = TRISOMI_TRESHOLDS["hard_min"]["NCV"]
    hard_max = TRISOMI_TRESHOLDS["hard_max"]["NCV"]
    soft_min = TRISOMI_TRESHOLDS["soft_min"]["NCV"]

    if (soft_max <= z_score < hard_max) or (hard_min < z_score <= soft_min):
        return "warning"
    elif (z_score >= hard_max) or (z_score <= hard_min):
        return "danger"
    else:
        return "default"


def get_scatter_data_for_coverage_plot(
    samples: List[DataBaseSample],
) -> Dict["str", CoveragePlotSampleData]:
    """Coverage Ratio data for Coverage Plot.
    Only adding samples with a zscore warning"""

    data = {}
    for sample in samples:
        sample_warnings: SampleWarning = get_sample_warnings(sample=sample)
        zscore_warnings = [
            sample_warnings.Zscore_13,
            sample_warnings.Zscore_18,
            sample_warnings.Zscore_21,
        ]
        if set(zscore_warnings) == {"default"}:
            continue

        x = []
        y = []
        for chromosome in range(1, 23):
            ratio = sample.dict().get(f"Chr{chromosome}_Ratio")
            if ratio is None:
                continue
            y.append(ratio)
            x.append(chromosome)
        data[sample.sample_id] = CoveragePlotSampleData(x_axis=x, y_axis=y)
    return data


def get_box_data_for_coverage_plot(samples: List[DataBaseSample]) -> Dict[int, List[float]]:
    """Coverage Ratio data for Coverage Plot."""

    data = {}
    for chromosome in range(1, 23):
        data[chromosome] = []
        for sample in samples:
            ratio = sample.dict().get(f"Chr{chromosome}_Ratio")
            if ratio is None:
                continue
            data[chromosome].append(ratio)
    return data


def get_ff_control_normal(adapter: NiptAdapter):
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
                "names": {"$push": "$sample_id"},
                "count": {"$sum": 1},
            }
        },
    ]
    relevant_aggregation_data = list(find.sample_aggregate(pipe=pipe, adapter=adapter))[0]
    return FetalFraction(**relevant_aggregation_data)


def ff_control_abnormal_pipe(abn: str) -> List[Dict]:
    return [
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
                "names": {"$push": "$sample_id"},
                "count": {"$sum": 1},
            }
        },
    ]


def get_ff_control_abnormal(adapter: NiptAdapter) -> FetalFractionControlAbNormal:
    """Abnormal Control Samples for fetal_fraction_XY plot"""

    plot_data = {}
    for abn in CHROM_ABNORM:
        plot_data[abn] = {}
        pipe = ff_control_abnormal_pipe(abn)
        statuses = {}
        for status_dict in find.sample_aggregate(pipe=pipe, adapter=adapter):
            status: str = status_dict["_id"][f"status_{abn}"]
            statuses[status] = status_dict

        plot_data[abn] = FetalFractionStatus(status_data_=statuses)
    return FetalFractionControlAbNormal(**plot_data)


def get_ff_cases(adapter, batch_id):
    """Cases for fetal fraction plot"""

    pipe = [
        {
            "$match": {
                "batch_id": {"$eq": batch_id},
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
                "names": {"$push": "$sample_id"},
            }
        },
    ]
    aggregation = list(find.sample_aggregate(pipe=pipe, adapter=adapter))

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
        {"$match": {f"status_{chr}": {"$eq": "Normal"}, "include": {"$eq": True}}},
        {
            "$group": {
                "_id": {f"status_{chr}": f"$status_{chr}"},
                "values": {"$push": f"$Zscore_{chr}"},
                "names": {"$push": "$sample_id"},
                "count": {"$sum": 1},
            }
        },
    ]
    if not list(find.sample_aggregate(pipe=pipe, adapter=adapter)):
        return {}
    data = find.sample_aggregate(pipe=pipe, adapter=adapter)[0]
    data["values"] = [value for value in data.get("values", [])]

    return data


def get_tris_control_abnormal(adapter, chr, x_axis):
    """Abnormal Control Samples for trisomi plots"""

    plot_data = {}

    pipe = [
        {
            "$match": {
                f"status_{chr}": {"$ne": "Normal", "$exists": "True"},
                "include": {"$eq": True},
            }
        },
        {
            "$group": {
                "_id": {f"status_{chr}": f"$status_{chr}"},
                "values": {"$push": f"$Zscore_{chr}"},
                "names": {"$push": "$sample_id"},
                "count": {"$sum": 1},
            }
        },
    ]

    for status_dict in find.sample_aggregate(pipe=pipe, adapter=adapter):
        status = status_dict["_id"][f"status_{chr}"]
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
        {"$match": {"batch_id": {"$eq": batch_id}, "include": {"$eq": True}}},
        {
            "$group": {
                "_id": {"batch": "$batch_id"},
                "values": {"$push": f"$Zscore_{chr}"},
                "names": {"$push": "$sample_id"},
                "count": {"$sum": 1},
            }
        },
    ]

    if not list(find.sample_aggregate(pipe=pipe, adapter=adapter)):
        return {}

    data = list(find.sample_aggregate(pipe=pipe, adapter=adapter))[0]
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

    batch_sort_aggregation = [{"$sort": {"SequencingDate": -1}}]
    sorted_batches = list(find.batch_aggregate(pipe=batch_sort_aggregation, adapter=adapter))
    if len(sorted_batches) > nr:
        sorted_batches = sorted_batches[0:nr]

    return sorted_batches


# Statistics


def get_statistics_for_scatter_plot(batches: list, fields: list) -> dict:
    """Formating data for scatter plot"""

    scatter_plot_data = {}
    for batch in batches:
        batch_id = batch.get("batch_id")
        scatter_plot_data[batch_id] = {"date": batch.get("SequencingDate")}

        for field in fields:
            scatter_plot_data[batch_id][field] = batch.get(field)

    return scatter_plot_data


def get_statistics_for_box_plot(adapter, batches: list, fields: list):
    """Getting and formating data for box plot"""

    match = {"$match": {"batch_id": {"$in": batches}}}
    lookup = {
        "$lookup": {
            "from": "batch",
            "localField": "batch_id",
            "foreignField": "batch_id",
            "as": "batch",
        }
    }
    unwind = {"$unwind": {"path": "$batch"}}
    group = {"$group": {"_id": {"batch": "$batch_id", "date": "$batch.SequencingDate"}}}

    for field in fields:
        group["$group"][field] = {"$push": f"${field}"}

    pipe = [match, lookup, unwind, group]
    # maybe add a fina sort to the pipe
    box_plot_data = list(find.sample_aggregate(pipe=pipe, adapter=adapter))

    return box_plot_data
