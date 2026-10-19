"""Basic economic formulas (first version, day 1)."""


def crf(rate: float, years: int) -> float:
    """Capital recovery factor: r(1+r)^n / ((1+r)^n - 1)."""
    if rate == 0:
        return 1.0 / years
    growth = (1.0 + rate) ** years
    return rate * growth / (growth - 1.0)


def annualized_cost(capex: float, opex_fraction: float, rate: float, years: int) -> float:
    """Annual cost = CAPEX * CRF + OPEX (opex_fraction of CAPEX per year)."""
    return capex * crf(rate, years) + capex * opex_fraction


def lcoe(annual_cost: float, annual_energy_kwh: float) -> float:
    """Cost per kWh. Same currency as annual_cost."""
    if annual_energy_kwh <= 0:
        raise ValueError("annual_energy_kwh must be positive")
    return annual_cost / annual_energy_kwh
