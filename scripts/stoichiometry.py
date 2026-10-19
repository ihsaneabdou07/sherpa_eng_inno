"""Check process ratios from molar masses (g/mol). Run: python scripts/stoichiometry.py"""
M_H2, M_H2O, M_NH3, M_CO2, M_CH3OH = 2.016, 18.015, 17.031, 44.010, 32.042

water_per_kg_h2 = M_H2O / M_H2                # 2 H2O -> 2 H2 + O2
h2_per_kg_nh3 = 3 * M_H2 / (2 * M_NH3)        # N2 + 3 H2 -> 2 NH3
h2_per_kg_meoh = 3 * M_H2 / M_CH3OH           # CO2 + 3 H2 -> CH3OH + H2O
co2_per_kg_meoh = M_CO2 / M_CH3OH

print(f"water per kg H2     : {water_per_kg_h2:.2f} kg (~{water_per_kg_h2:.1f} L)")
print(f"H2 per kg NH3       : {h2_per_kg_nh3:.3f} kg")
print(f"H2 per kg methanol  : {h2_per_kg_meoh:.3f} kg")
print(f"CO2 per kg methanol : {co2_per_kg_meoh:.3f} kg")
