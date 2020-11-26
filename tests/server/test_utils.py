from NIPTool.server.utils import (
    get_last_batches,
    get_statistics_for_box_plot,
    get_statistics_for_scatter_plot,
)


def test_get_last_batches(mock_app):
    # GIVEN a database with four batch documents:
    batch1 = {"SequencingDate": "2022-03-10"}
    batch2 = {"SequencingDate": "2022-02-10"}
    batch3 = {"SequencingDate": "2022-02-09"}
    batch4 = {"SequencingDate": "2021-03-10"}

    mock_app.db.batch.insert_many([batch4, batch1, batch3, batch2])

    # WHEN running get_last_batches with nr=3
    results = get_last_batches(adapter=mock_app.adapter, nr=3)

    # THEN the results should contain the thre batches with the latest
    # SequencingDate, sorted by SequencingDate
    assert results == [batch1, batch2, batch3]


def test_get_last_batches_to_fiew_batches_in_database(mock_app):
    # GIVEN a database with four batch documents:
    batch1 = {"SequencingDate": "2022-03-10"}
    batch2 = {"SequencingDate": "2022-02-10"}
    batch3 = {"SequencingDate": "2022-02-09"}
    batch4 = {"SequencingDate": "2021-03-10"}

    mock_app.db.batch.insert_many([batch4, batch1, batch3, batch2])

    # WHEN running get_last_batches with nr=5
    results = get_last_batches(adapter=mock_app.adapter, nr=5)

    # THEN the results should contain the four batches in the
    # database sorted by SequencingDate
    assert results == [batch1, batch2, batch3, batch4]


def test_get_statistics_for_box_plot(mock_app, small_helpers):
    # GIVEN a database with thre batches and nine samples like below
    batches = ["201860", "201861", "201862"]
    for batch_id in batches:
        batch = small_helpers.batch(batch_id=batch_id)
        mock_app.db.batch.insert_one(batch)
        for i in [1, 2, 3]:
            sample = small_helpers.sample(
                sample_id=batch_id + str(i),
                batch_id=batch_id,
                ratio_13=i,
                fetal_fraction=i)
            mock_app.db.sample.insert_one(sample)

    # WHEN running get_statistics_for_box_plot
    results = get_statistics_for_box_plot(
        adapter=mock_app.adapter,
        batches=batches,
        fields=["Ratio_13", "FF_Formatted"],
    )

    # THEN the results shoule be:
    for index, result in enumerate(results):
        assert result == {
            "FF_Formatted": [1, 2, 3],
            "Ratio_13": [1, 2, 3],
            "_id": {"batch": batches[index], "date": "2022-03-10"},
        }


def test_get_statistics_for_scatter_plot(small_helpers):
    # GIVEN a list with three batch documents:
    batches = [
        small_helpers.batch(batch_id="201860", stdev_13=0.02, stdev_21=0.01),
        small_helpers.batch(batch_id="201861", stdev_13=0.01, stdev_21=0.09),
        small_helpers.batch(batch_id="201862", stdev_13=0.05, stdev_21=0.08),
    ]

    # WHEN running get_statistics_for_scatter_plot
    results = get_statistics_for_scatter_plot(
        batches=batches, fields=["Stdev_13", "Stdev_21"]
    )

    # THEN the results should look like this:
    expected_result = {
        "201860": {"date": "2022-03-10", "Stdev_13": 0.02, "Stdev_21": 0.01},
        "201861": {"date": "2022-03-10", "Stdev_13": 0.01, "Stdev_21": 0.09},
        "201862": {"date": "2022-03-10", "Stdev_13": 0.05, "Stdev_21": 0.08},
    }
    assert results == expected_result
