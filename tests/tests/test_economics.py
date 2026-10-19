import pytest
from economics.efuel_economics import EFuelEconomics

def test_lcoe_calculation():
    model = EFuelEconomics(price_elec=30)
    result = model.calculate_lcoe(
        product_name='e-methanol',
        capex_synthese_eur_kw=750,
        h2_ratio=0.1875,
        co2_ratio=1.375
    )
    assert result['total_lcoe_eur_t'] > 0
    assert 'cost_h2' in result
    print(f"LCOE e-methanol: {result['total_lcoe_eur_t']:.2f} €/t")
