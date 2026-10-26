"""Offline tests for the Thompson sampling budget allocator."""

import pytest

from services.trading.thompson_allocator import (
    PlatformPosterior,
    ThompsonSamplingAllocator,
)


def _patch_samples(monkeypatch, samples):
    def fake_sample(self):
        return samples[self.platform]

    monkeypatch.setattr(PlatformPosterior, "sample", fake_sample)


def test_update_shifts_the_beta_posterior():
    allocator = ThompsonSamplingAllocator()
    allocator.initialize_platforms(["meta", "google"])

    allocator.update_posterior("meta", conversions=8, non_converting_spend=2)
    stats = allocator.get_platform_statistics()

    assert stats["meta"]["alpha"] == pytest.approx(10.0)
    assert stats["meta"]["beta"] == pytest.approx(4.0)
    assert stats["meta"]["total_conversions"] == pytest.approx(8.0)
    assert stats["meta"]["total_failures"] == pytest.approx(2.0)
    assert stats["meta"]["mean"] == pytest.approx(10 / 14)
    # The untouched platform keeps the Beta(2, 2) prior.
    assert stats["google"]["alpha"] == pytest.approx(2.0)
    assert stats["google"]["beta"] == pytest.approx(2.0)


def test_allocation_is_proportional_to_the_draw(monkeypatch):
    allocator = ThompsonSamplingAllocator()
    allocator.initialize_platforms(["meta", "google", "thrad"])
    _patch_samples(monkeypatch, {"meta": 0.5, "google": 0.3, "thrad": 0.2})

    allocation = allocator.thompson_allocate(100.0)

    assert allocation["meta"].allocated_budget == pytest.approx(50.0)
    assert allocation["google"].allocated_budget == pytest.approx(30.0)
    assert allocation["thrad"].allocated_budget == pytest.approx(20.0)
    assert sum(item.allocated_budget for item in allocation.values()) == pytest.approx(100.0)


def test_floor_is_applied(monkeypatch):
    allocator = ThompsonSamplingAllocator()
    allocator.initialize_platforms(["meta", "google"])
    _patch_samples(monkeypatch, {"meta": 0.9, "google": 0.1})

    allocation = allocator.thompson_allocate(100.0, floors={"google": 25.0})

    assert allocation["google"].raw_allocation == pytest.approx(10.0)
    assert allocation["google"].allocated_budget == pytest.approx(25.0)
    assert allocation["google"].floor == pytest.approx(25.0)


def test_cap_then_equal_split_of_what_is_left(monkeypatch):
    allocator = ThompsonSamplingAllocator()
    allocator.initialize_platforms(["meta", "google", "thrad"])
    _patch_samples(monkeypatch, {"meta": 0.5, "google": 0.4, "thrad": 0.1})

    allocation = allocator.thompson_allocate(
        100.0,
        caps={"meta": 20.0, "google": 100.0, "thrad": 100.0},
    )

    # Meta is capped at 20. The leftover 30 is split equally across the other two.
    assert allocation["meta"].allocated_budget == pytest.approx(20.0)
    assert allocation["google"].allocated_budget == pytest.approx(55.0)
    assert allocation["thrad"].allocated_budget == pytest.approx(25.0)
    assert sum(item.allocated_budget for item in allocation.values()) == pytest.approx(100.0)


def test_allocate_without_platforms_raises():
    with pytest.raises(ValueError, match="No platforms initialized"):
        ThompsonSamplingAllocator().thompson_allocate(100.0)
