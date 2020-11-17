#!/usr/bin/env python

from flask import (
    url_for,
    redirect,
    render_template,
    request,
    Blueprint,
    current_app,
    session,
    flash,
)
from flask_login import login_required
from datetime import datetime
from NIPTool.server.utils import *
from NIPTool.server.constants import *
from flask_weasyprint import HTML, render_pdf


app = current_app
server_bp = Blueprint("server", __name__)


@server_bp.route("/", methods=["GET", "POST"])
def index():
    """Log in view."""
    user = session.get("user")
    if user:
        return redirect(url_for("server.batches"))
    return render_template("index.html", user=user)


@server_bp.route("/batches")
@login_required
def batches():
    """List of all batches"""
    all_batches = list(app.adapter.batches())
    return render_template("batches.html", batches=all_batches)


### Batch tabs

@server_bp.route("/batches/<batch_id>/")
@login_required
def batch(batch_id):
    """Batch view with table of all samples in the batch."""
    samples = app.adapter.batch_samples(batch_id)
    return render_template(
        "batch/tabs/table.html",
        batch=app.adapter.batch(batch_id),
        sample_info=[get_sample_info(sample) for sample in samples],
        page_id="batches",
    )


@server_bp.route("/batches/<batch_id>/NCV13")
@login_required
def NCV13(batch_id):
    """Batch view with with NCV-13 plot"""
    return render_template(
        "batch/tabs/NCV.html",
        batch=app.adapter.batch(batch_id),
        chr="13",
        ncv_chrom_data={"13": get_tris_cases(app.adapter, "13", batch_id)},
        normal_data=get_tris_control_normal(app.adapter, "13"),
        abnormal_data=get_tris_control_abnormal(app.adapter, "13", 0),
        page_id="batches_NCV13",
    )


@server_bp.route("/batches/<batch_id>/NCV18")
@login_required
def NCV18(batch_id):
    """Batch view with with NCV-18 plot"""
    return render_template(
        "batch/tabs/NCV.html",
        batch=app.adapter.batch(batch_id),
        chr="18",
        ncv_chrom_data={"18": get_tris_cases(app.adapter, "18", batch_id)},
        normal_data=get_tris_control_normal(app.adapter, "18"),
        abnormal_data=get_tris_control_abnormal(app.adapter, "18", 0),
        page_id="batches_NCV18",
    )


@server_bp.route("/batches/<batch_id>/NCV21")
@login_required
def NCV21(batch_id):
    """Batch view with NCV-21 plot"""
    return render_template(
        "batch/tabs/NCV.html",
        batch=app.adapter.batch(batch_id),
        chr="21",
        ncv_chrom_data={"21": get_tris_cases(app.adapter, "21", batch_id)},
        normal_data=get_tris_control_normal(app.adapter, "21"),
        abnormal_data=get_tris_control_abnormal(app.adapter, "21", 0),
        page_id="batches_NCV21",
    )


@server_bp.route("/batches/<batch_id>/fetal_fraction_XY")
@login_required
def fetal_fraction_XY(batch_id):
    """Batch view with fetal fraction (X against Y) plot"""
    batch = app.adapter.batch(batch_id)
    control = get_ff_control_normal(app.adapter)
    abnormal = get_ff_control_abnormal(app.adapter)
    return render_template(
        "batch/tabs/FF_XY.html",
        control=control,
        abnormal=abnormal,
        cases=get_ff_cases(app.adapter, batch_id),
        max_x=max(control["FFX"]) + 1,
        min_x=min(control["FFX"]) - 1,
        batch=batch,
        page_id="batches_FF_XY",
    )


@server_bp.route("/batches/<batch_id>/fetal_fraction")
@login_required
def fetal_fraction(batch_id):
    """Batch view with fetal fraction plot"""
    batch = app.adapter.batch(batch_id)
    return render_template(
        "batch/tabs/FF.html",
        control=get_ff_control_normal(app.adapter),
        cases=get_ff_cases(app.adapter, batch_id),
        batch=batch,
        page_id="batches_FF",
    )


@server_bp.route("/batches/<batch_id>/coverage")
@login_required
def coverage(batch_id):
    """Batch view with coverage plot"""
    batch = app.adapter.batch(batch_id)
    samples = list(app.adapter.batch_samples(batch_id))
    scatter_data = get_scatter_data_for_coverage_plot(samples)
    box_data = get_box_data_for_coverage_plot(samples)
    return render_template(
        "batch/tabs/coverage.html",
        batch=batch,
        x_axis=list(range(1, 23)),
        scatter_data=scatter_data,
        box_data=box_data,
        page_id="batches_cov",
    )


# Report

@server_bp.route("/batches/<batch_id>/report/<coverage>")
@login_required
def report(batch_id, coverage):
    """Report view, collecting all tables and plots from one batch."""

    batch = app.adapter.batch(batch_id)
    samples = list(app.adapter.batch_samples(batch_id))
    scatter_data = get_scatter_data_for_coverage_plot(samples)
    box_data = get_box_data_for_coverage_plot(samples)
    control = get_ff_control_normal(app.adapter)

    report_html = render_template(
        "batch/report_to_pdf.html",
        batch=batch,
        # NCV
        ncv_chrom_data={
            "13": get_tris_cases(app.adapter, "13", batch_id),
            "18": get_tris_cases(app.adapter, "18", batch_id),
            "21": get_tris_cases(app.adapter, "21", batch_id),
        },
        normal_data=get_tris_control_normal(app.adapter, "21"),
        abnormal_data=get_tris_control_abnormal(app.adapter, "21", 0),
        # FF
        control=control,
        cases=get_ff_cases(app.adapter, batch_id),
        abnormal=get_ff_control_abnormal(app.adapter),
        max_x=max(control["FFX"]) + 1,
        min_x=min(control["FFX"]) - 1,
        # table
        sample_info=[get_sample_info(sample) for sample in samples],
        # coverage
        x_axis=list(range(1, 23)),
        scatter_data=scatter_data,
        box_data=box_data,
        page_id="batches",

    )
    return render_pdf(
        HTML(string=report_html),
        download_filename='report.pdf',
    )



### Sample Views


@server_bp.route("/samples/<sample_id>/")
@login_required
def sample(sample_id):
    """Sample view with sample information."""
    sample = app.adapter.sample(sample_id)
    batch = app.adapter.batch(sample.get("SampleProject"))

    return render_template(
        "sample/sample.html",
        chrom_abnorm=CHROM_ABNORM,
        sample=sample,
        status_classes=STATUS_CLASSES,
        batch=batch,
    )


@server_bp.route("/samples/<sample_id>/tris")
@login_required
def sample_tris(sample_id):
    """Sample view with trisomi plot."""
    sample = app.adapter.sample(sample_id)
    batch = app.adapter.batch(sample.get("SampleProject"))
    abnormal_data, data_per_abnormaliy = get_abn_for_samp_tris_plot(app.adapter)
    normal_data = get_normal_for_samp_tris_plot(app.adapter)
    sample_data = get_sample_for_samp_tris_plot(sample)
    return render_template(
        "sample/sample_tris.html",
        tris_abn=data_per_abnormaliy,
        normal_data=normal_data,
        abnormal_data=abnormal_data,
        sample_data=sample_data,
        sample=sample,
        batch=batch,
        status_colors=STATUS_COLORS,
        page_id="sample_tris",
    )


# Statistics


@server_bp.route("/statistics")
@login_required
def statistics():
    """Statistics view."""

    nr_batches = 3
    scatter_plots = ["Stdev_13", "Stdev_18", "Stdev_21"]
    box_plots = [
        "Chr13_Ratio",
        "Chr18_Ratio",
        "Chr21_Ratio",
        "FF_Formatted",
        "DuplicationRate",
        "MappedReads",
        "GC_Dropout",
    ]

    batches = get_last_batches(adapter=app.adapter, nr=nr_batches)
    batch_ids = [batch.get("_id") for batch in batches]
    box_stat = get_statistics_for_box_plot(
        adapter=app.adapter, batches=batch_ids, fields=box_plots
    )
    scatter_stat = get_statistics_for_scatter_plot(
        batches=batches, fields=scatter_plots
    )
    return render_template(
        "statistics.html",
        ticks=list(range(1, nr_batches + 1)),
        nr_batches=nr_batches,
        batch_ids=batch_ids,
        box_stat=box_stat,
        box_plots=box_plots,
        scatter_stat=scatter_stat,
        scatter_plots=scatter_plots,
    )


### Udate


@server_bp.route("/update", methods=["POST"])
@login_required
def update():
    """Update the database"""
    time_stamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    user = app.user
    if user.role != "RW":
        return "", 201

    if request.form.get("form_id") == "set_sample_status":
        sample_id = request.form["sample_id"]
        sample = app.adapter.sample(sample_id)
        for abnormality in CHROM_ABNORM:
            new_abnormality_status = request.form[abnormality]
            if sample.get(f"status_{abnormality}") != new_abnormality_status:
                sample[f"status_{abnormality}"] = new_abnormality_status
                sample[f"status_change_{abnormality}"] = " ".join(
                    [user.name, time_stamp]
                )
        app.adapter.add_or_update_document(sample, app.adapter.sample_collection)

    if request.form.get("form_id") == "set_sample_comment":
        sample_id = request.form["sample_id"]
        sample = app.adapter.sample(sample_id)
        if request.form.get("comment") != sample.get("comment"):
            sample["comment"] = request.form.get("comment")
        app.adapter.add_or_update_document(sample, app.adapter.sample_collection)

    if request.form.get("button_id") == "Save":
        samples = request.form.getlist("samples")
        for sample_id in samples:
            sample = app.adapter.sample(sample_id)
            comment = request.form.get(f"comment_{sample_id}")
            include = request.form.get(f"include_{sample_id}")
            if comment != sample.get("comment"):
                sample["comment"] = comment
            if include and sample.get("include", False) == False:
                sample["include"] = True
                sample["change_include_date"] = " ".join([user.name, time_stamp])
            elif not include and sample.get("include") == True:
                sample["include"] = False
            app.adapter.add_or_update_document(sample, app.adapter.sample_collection)

    if request.form.get("button_id") == "include all samples":
        samples = request.form.getlist("samples")
        for sample_id in samples:
            sample = app.adapter.sample(sample_id)
            if sample.get("include", False) == False:
                sample["include"] = True
                sample["change_include_date"] = " ".join([user.name, time_stamp])
                app.adapter.add_or_update_document(
                    sample, app.adapter.sample_collection
                )

    return redirect(request.referrer)
