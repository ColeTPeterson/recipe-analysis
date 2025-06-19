#!/usr/bin/env python3
"""
Recipe DAG Demonstration

This file tests all of the basic components of a recipe DAG
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from models.recipe import Recipe
from models.symbol import Symbol, SymbolType
from models.item import Ingredient, Equipment
from models.measurement import MeasurementAbs

def create_symbols():
    actions = {
        'boil': Symbol(SymbolType.ACTION, {"COOKING_METHOD", "TEMPERATURE_CHANGE_INCREASE"}, "boil", {"cook"}, "Boil in water"),
        'chop_1': Symbol(SymbolType.ACTION, {"PREPARATION_TASK", "DIVISION"}, "chop_1", {"dice", "cut"}, "Cut into pieces"),
        'chop_2': Symbol(SymbolType.ACTION, {"PREPARATION_TASK", "DIVISION"}, "chop_2", {"dice", "cut"}, "Cut into pieces"),
        'chop_3': Symbol(SymbolType.ACTION, {"PREPARATION_TASK", "DIVISION"}, "chop_3", {"dice", "cut"}, "Cut into pieces"),
        'saute': Symbol(SymbolType.ACTION, {"COOKING_METHOD", "TEMPERATURE_CHANGE_INCREASE"}, "saute", {"fry"}, "Cook with oil"),
        'simmer': Symbol(SymbolType.ACTION, {"COOKING_METHOD", "TEMPERATURE_CHANGE_INCREASE"}, "simmer", {"cook_slowly"}, "Cook gently"),
        'strain': Symbol(SymbolType.ACTION, {"SEPARATION"}, "strain", {"strain"}, "Separate liquid from solid"),
        'combine': Symbol(SymbolType.ACTION, {"COMBINATION"}, "combine", {"mix"}, "Combine ingredients"),
        'season': Symbol(SymbolType.ACTION, {"PREPARATION_TASK", "COMBINATION"}, "season", {"add_seasoning"}, "Add seasonings"),
        'toss': Symbol(SymbolType.ACTION, {"COMBINATION"}, "toss", {"mix_final"}, "Toss ingredients together")
    }
    
    ingredients = {
        'pasta': Symbol(SymbolType.INGREDIENT_IDENTITY, {"GRAIN", "GRAIN_CEREAL_WHEAT"}, "pasta", {"noodles"}, "Wheat pasta"),
        'tomato': Symbol(SymbolType.INGREDIENT_IDENTITY, {"VEGETABLE", "FRUIT"}, "tomato", {"tomatoes"}, "Fresh tomatoes"),
        'onion': Symbol(SymbolType.INGREDIENT_IDENTITY, {"VEGETABLE", "VEGETABLE_ROOT"}, "onion", {"onions"}, "Yellow onion"),
        'garlic': Symbol(SymbolType.INGREDIENT_IDENTITY, {"VEGETABLE", "HERB"}, "garlic", {"garlic_clove"}, "Fresh garlic"),
        'oil': Symbol(SymbolType.INGREDIENT_IDENTITY, {"FAT"}, "olive_oil", {"oil"}, "Extra virgin olive oil"),
        'water': Symbol(SymbolType.INGREDIENT_IDENTITY, {"LIQUID"}, "water", {"h2o"}, "Water"),
        'salt': Symbol(SymbolType.INGREDIENT_IDENTITY, {"SPICE"}, "salt", {"table_salt"}, "Table salt"),
        'basil': Symbol(SymbolType.INGREDIENT_IDENTITY, {"HERB"}, "basil", {"fresh_basil"}, "Fresh basil")
    }
    
    equipment = {
        'pot': Symbol(SymbolType.EQUIPMENT_IDENTITY, {"VESSEL_COOKWARE"}, "large_pot", {"pot"}, "Large cooking pot"),
        'pan': Symbol(SymbolType.EQUIPMENT_IDENTITY, {"VESSEL_COOKWARE"}, "frying_pan", {"pan", "skillet"}, "Frying pan"),
        'knife': Symbol(SymbolType.EQUIPMENT_IDENTITY, {"TOOL_CUTTING"}, "chef_knife", {"knife"}, "Chef's knife"),
        'colander': Symbol(SymbolType.EQUIPMENT_IDENTITY, {"TOOL_STRAINING"}, "colander", {"strainer"}, "Colander for draining")
    }
    
    return {**actions, **ingredients, **equipment}

def create_items(symbols):
    """Create ingredients and equipment for recipe."""
    # Unit symbols
    cup_unit = Symbol(SymbolType.UNIT, {"VOLUME"}, "cup", {"c"}, "Volume unit")
    tbsp_unit = Symbol(SymbolType.UNIT, {"VOLUME"}, "tablespoon", {"tbsp"}, "Tablespoon")
    clove_unit = Symbol(SymbolType.UNIT, {"COUNT"}, "clove", {"cloves"}, "Individual clove")
    
    # Base ingredients
    items = {
        'pasta_dry': Ingredient("dry_pasta", {symbols['pasta']}, None, None, None, None, 1, None, None, 
                               MeasurementAbs(1.0, cup_unit), False, False),
        'fresh_tomatoes': Ingredient("fresh_tomatoes", {symbols['tomato']}, None, None, None, None, 2, None, None,
                                   MeasurementAbs(4.0, Symbol(SymbolType.UNIT, {"COUNT"}, "piece", {"pieces"}, "Individual item")), False, False),
        'onion_whole': Ingredient("whole_onion", {symbols['onion']}, None, None, None, None, 3, None, None,
                                MeasurementAbs(1.0, Symbol(SymbolType.UNIT, {"COUNT"}, "piece", {"pieces"}, "Individual item")), False, False),
        'garlic_cloves': Ingredient("garlic_cloves", {symbols['garlic']}, None, None, None, None, 4, None, None,
                                 MeasurementAbs(3.0, clove_unit), False, False),
        'olive_oil': Ingredient("olive_oil", {symbols['oil']}, None, None, None, None, 5, None, None,
                              MeasurementAbs(2.0, tbsp_unit), False, False),
        'water': Ingredient("water", {symbols['water']}, None, None, None, None, 6, None, None,
                          MeasurementAbs(8.0, cup_unit), False, False),
        'salt': Ingredient("salt", {symbols['salt']}, None, None, None, None, 7, None, None,
                         MeasurementAbs(1.0, Symbol(SymbolType.UNIT, {"VOLUME"}, "teaspoon", {"tsp"}, "Teaspoon")), False, False),
        'basil': Ingredient("fresh_basil", {symbols['basil']}, None, None, None, None, 8, None, None,
                          MeasurementAbs(0.25, cup_unit), False, False)
    }
    
    # Intermediate products
    items.update({
        'onion_chopped': Ingredient("chopped_onion", {symbols['onion']}, None, None, None, None, 10, None, None, None, False, False),
        'garlic_chopped': Ingredient("chopped_garlic", {symbols['garlic']}, None, None, None, None, 11, None, None, None, False, False),
        'tomatoes_chopped': Ingredient("chopped_tomatoes", {symbols['tomato']}, None, None, None, None, 12, None, None, None, False, False),
        'pasta_cooked': Ingredient("cooked_pasta", {symbols['pasta']}, None, None, None, None, 13, None, None, None, False, False),
        'pasta_drained': Ingredient("drained_pasta", {symbols['pasta']}, None, None, None, None, 14, None, None, None, False, False),
        'pasta_water': Ingredient("pasta_water", {symbols['water']}, None, None, None, None, 15, None, None, None, False, False),
        'aromatics_sauteed': Ingredient("sauteed_aromatics", {symbols['onion'], symbols['garlic']}, None, None, None, None, 16, None, None, None, False, False),
        'sauce_base': Ingredient("sauce_base", {symbols['tomato']}, None, None, None, None, 17, None, None, None, False, False),
        'marinara_sauce': Ingredient("marinara_sauce", {symbols['tomato']}, None, None, None, None, 18, None, None, None, False, False),
        'seasoned_marinara': Ingredient("seasoned_marinara", {symbols['tomato']}, None, None, None, None, 19, None, None, None, False, False),
        'pasta_with_sauce': Ingredient("pasta_with_marinara", {symbols['pasta'], symbols['tomato']}, None, None, None, None, 20, None, None, None, False, False)
    })
    
    # Equipment
    items.update({
        'large_pot': Equipment("large_pot", {symbols['pot']}, None, None, None, None, 1),
        'frying_pan': Equipment("frying_pan", {symbols['pan']}, None, None, None, None, 2),
        'chef_knife': Equipment("chef_knife", {symbols['knife']}, None, None, None, None, 3),
        'colander': Equipment("colander", {symbols['colander']}, None, None, None, None, 4)
    })
    
    return items

def build_recipe_dag():
    """Build a pasta recipe DAG with parallel operations."""
    print("=== Building Pasta Recipe DAG ===")
    
    symbols = create_symbols()
    items = create_items(symbols)
    
    # Create recipe
    recipe = Recipe(
        recipe_id=2,
        title="Pasta with Marinara Sauce",
        root_instructions=set(),
        all_instructions=set()
    )
    
    # Add all items and actions
    for item in items.values():
        recipe.add_item_node(item)
    
    print("Adding actions to recipe...")
    for symbol_name in ['chop_1', 'chop_2', 'chop_3', 'boil', 'saute', 'simmer', 'strain', 'combine', 'season', 'toss']:
        print(f"Adding action: {symbol_name} -> {symbols[symbol_name].canonical_form}")
        recipe.add_action_node(symbols[symbol_name])
    
    print(f"Recipe now has {len(recipe.action_nodes)} action nodes")
    for action in recipe.action_nodes:
        print(f"  - {action.canonical_form} (object id: {id(action)})")
    
    print("Building DAG connections...")
    
    print("Available items:", list(items.keys()))
    print("Available symbols:", list(symbols.keys()))
    
    print("\n=== DEBUGGING ITEM NAMES ===")
    for key, item in items.items():
        print(f"Key: '{key}' -> Item name: '{item.name}'")
    
    # Chop onion (chop instance 1)
    items['onion_whole'].add_consuming_action(symbols['chop_1'])
    items['chef_knife'].add_consuming_action(symbols['chop_1'])
    items['onion_chopped'].add_producing_action(symbols['chop_1'])
    
    # Chop garlic (chop instance 2)
    items['garlic_cloves'].add_consuming_action(symbols['chop_2'])
    items['chef_knife'].add_consuming_action(symbols['chop_2'])
    items['garlic_chopped'].add_producing_action(symbols['chop_2'])
    
    # Chop tomatoes (chop instance 3)
    items['fresh_tomatoes'].add_consuming_action(symbols['chop_3'])
    items['chef_knife'].add_consuming_action(symbols['chop_3'])
    items['tomatoes_chopped'].add_producing_action(symbols['chop_3'])
    
    # Boil pasta
    items['pasta_dry'].add_consuming_action(symbols['boil'])
    items['water'].add_consuming_action(symbols['boil'])
    items['salt'].add_consuming_action(symbols['boil'])
    items['large_pot'].add_consuming_action(symbols['boil'])
    items['pasta_cooked'].add_producing_action(symbols['boil'])
    
    # Strain pasta - SEPARATION produces two outputs
    items['pasta_cooked'].add_consuming_action(symbols['strain'])
    items['colander'].add_consuming_action(symbols['strain'])
    items['pasta_drained'].add_producing_action(symbols['strain'])
    items['pasta_water'].add_producing_action(symbols['strain'])
    
    # Saute aromatics (only onion and garlic, not tomatoes)
    items['onion_chopped'].add_consuming_action(symbols['saute'])
    items['garlic_chopped'].add_consuming_action(symbols['saute'])
    items['olive_oil'].add_consuming_action(symbols['saute'])
    items['frying_pan'].add_consuming_action(symbols['saute'])
    items['aromatics_sauteed'].add_producing_action(symbols['saute'])
    
    # Add tomatoes to create sauce base
    items['aromatics_sauteed'].add_consuming_action(symbols['combine'])
    items['tomatoes_chopped'].add_consuming_action(symbols['combine'])
    items['sauce_base'].add_producing_action(symbols['combine'])
    
    # Simmer sauce
    items['sauce_base'].add_consuming_action(symbols['simmer'])
    items['marinara_sauce'].add_producing_action(symbols['simmer'])
    
    # Season sauce (creates new seasoned version)
    items['marinara_sauce'].add_consuming_action(symbols['season'])
    items['basil'].add_consuming_action(symbols['season'])
    items['seasoned_marinara'].add_producing_action(symbols['season'])
    
    # Final combination
    items['pasta_drained'].add_consuming_action(symbols['toss'])
    items['seasoned_marinara'].add_consuming_action(symbols['toss'])
    items['pasta_with_sauce'].add_producing_action(symbols['toss'])
    
    return recipe, symbols, items

def validate_all_connections(recipe, symbols, items):
    """Comprehensive validation to ensure ALL nodes are connected."""
    print("\n=== COMPREHENSIVE CONNECTION VALIDATION ===")
    
    disconnected_items = []
    disconnected_actions = []
    
    for item in recipe.item_nodes:
        if not item.is_operand():
            disconnected_items.append(item.name)
    
    for action in recipe.action_nodes:
        if len(action.input_nodes) == 0 and len(action.output_nodes) == 0:
            disconnected_actions.append(action.canonical_form)
    
    print(f"Disconnected items: {disconnected_items}")
    print(f"Disconnected actions: {disconnected_actions}")
    
    print("\n=== ITEM CONNECTION DETAILS ===")
    for item in recipe.item_nodes:
        consuming = [a.canonical_form for a in item.consuming_actions]
        producing = [a.canonical_form for a in item.producing_actions]
        print(f"{item.name}: consumed_by={consuming}, produced_by={producing}")
    
    print("\n=== ACTION CONNECTION DETAILS ===")
    for action in recipe.action_nodes:
        inputs = [item.name for item in action.input_nodes]
        outputs = [item.name for item in action.output_nodes]
        print(f"{action.canonical_form}: inputs={inputs}, outputs={outputs}")
    
    return len(disconnected_items) == 0 and len(disconnected_actions) == 0

def analyze_dag(recipe, symbols, items):
    """Analyze the DAG structure."""
    print("\n=== DAG Analysis ===")
    
    # Basic validation
    is_valid = recipe.validate_dag_structure()
    print(f"DAG Structure Valid: {is_valid}")
    print(f"Total Action Nodes: {len(recipe.action_nodes)}")
    print(f"Total Item Nodes: {len(recipe.item_nodes)}")
    
    print(f"\n=== Preparation Approach Analysis ===")
    
    # Show parallel paths
    print(f"\nParallel execution paths:")
    print(f"  Path 1: Pasta preparation (boil → strain)")
    print(f"  Path 2: Sauce preparation (3 chop instances → saute aromatics → combine with tomatoes → simmer → season)")
    print(f"  Convergence: Final toss of pasta + sauce")
    
    # Critical path analysis
    print(f"\n=== Critical Path Indicators ===")
    root_actions = recipe.get_root_action_nodes()
    leaf_actions = recipe.get_leaf_action_nodes()
    print(f"Root Actions (can start immediately): {[a.canonical_form for a in root_actions]}")
    print(f"Leaf Actions (final operations): {[a.canonical_form for a in leaf_actions]}")
    
    # Show transformation chains
    print(f"\n=== Transformation Chains ===")
    pasta_chain = ["dry_pasta", "cooked_pasta", "drained_pasta", "pasta_with_marinara"]
    sauce_chain = ["fresh_tomatoes", "chopped_tomatoes", "sauce_base", "marinara_sauce"]
    aromatics_chain = ["whole_onion + garlic_cloves", "chopped_onion + chopped_garlic", "sauteed_aromatics"]
    
    print(f"Pasta transformation: {' → '.join(pasta_chain)}")
    print(f"Sauce transformation: {' → '.join(sauce_chain)}")
    print(f"Aromatics transformation: {' → '.join(aromatics_chain)}")

def generate_dot_file(recipe, output_file="docs/Recipe DAG Example.dot"):
    """Generate DOT visualization for a recipe."""
    print(f"\n=== Generating Visualization ===")
    
    dot_content = [
        "digraph RecipeDAG {",
        "    rankdir=TB;",
        "    node [fontname=\"Arial\", fontsize=10];",
        "    edge [fontsize=8];",
        "",
        "    // Subgraphs for organization",
        "    subgraph cluster_ingredients {",
        "        label=\"Base Ingredients\";",
        "        style=dashed;",
        "        color=green;",
    ]
    
    # Add base ingredients to subgraph
    base_ingredients = [item for item in recipe.item_nodes 
                       if item.is_input_operand() and hasattr(item, 'ingredient_id')]
    for item in base_ingredients:
        dot_content.append(f'        "{item.name}" [shape=ellipse, fillcolor=lightgreen, style=filled];')
    
    dot_content.extend([
        "    }",
        "",
        "    subgraph cluster_equipment {",
        "        label=\"Equipment\";", 
        "        style=dashed;",
        "        color=blue;",
    ])
    
    # Add equipment
    equipment_items = [item for item in recipe.item_nodes if hasattr(item, 'equipment_id')]
    for item in equipment_items:
        dot_content.append(f'        "{item.name}" [shape=diamond, fillcolor=lightblue, style=filled];')
    
    dot_content.extend([
        "    }",
        "",
        "    // Intermediate and final products",
    ])
    
    # Add intermediate and final products
    for item in recipe.item_nodes:
        if not item.is_input_operand() and not hasattr(item, 'equipment_id'):
            if item.is_output_operand():
                color = "lightcoral"
            else:
                color = "lightyellow"
            dot_content.append(f'    "{item.name}" [shape=ellipse, fillcolor={color}, style=filled];')
    
    dot_content.extend([
        "",
        "    // Action nodes",
    ])
    
    action_name_map = {}
    
    for action in recipe.action_nodes:
        categories = action.categories
        if "PREPARATION_TASK" in categories:
            color = "lavender"
        elif "COOKING_METHOD" in categories:
            color = "lightsalmon"
        elif "COMBINATION" in categories:
            color = "lightcyan"
        else:
            color = "lightgray"
        
        node_name = action.canonical_form
        display_name = action.canonical_form
            
        action_name_map[action] = node_name
        dot_content.append(f'    "{node_name}" [label="{display_name}", shape=box, fillcolor={color}, style=filled];')
    
    dot_content.extend([
        "",
        "    // Edges",
    ])
    
    # Add all edges
    for action in recipe.action_nodes:
        action_node_name = action_name_map[action]
            
        for input_item in action.input_nodes:
            dot_content.append(f'    "{input_item.name}" -> "{action_node_name}";')
        for output_item in action.output_nodes:
            dot_content.append(f'    "{action_node_name}" -> "{output_item.name}";')
    
    dot_content.extend([
        "",
        "    subgraph cluster_legend {",
        "        label=\"Legend\";",
        "        style=filled;",
        "        fillcolor=white;",
        "        color=black;",
        "        fontsize=12;",
        "        fontname=\"Arial Bold\";",
        "        ",
        "        legend_input [label=\"Base Ingredient\\n(Recipe Input)\", shape=ellipse, fillcolor=lightgreen, style=filled, fontsize=10];",
        "        legend_intermediate [label=\"Intermediate Product\\n(Transformed Item)\", shape=ellipse, fillcolor=lightyellow, style=filled, fontsize=10];",
        "        legend_output [label=\"Final Product\\n(Recipe Output)\", shape=ellipse, fillcolor=lightcoral, style=filled, fontsize=10];",
        "        legend_equipment [label=\"Equipment\\n(Reusable Tool)\", shape=diamond, fillcolor=lightblue, style=filled, fontsize=10];",
        "        ",
        "        legend_prep [label=\"Preparation Task\\n(chop, season)\", shape=box, fillcolor=lavender, style=filled, fontsize=10];",
        "        legend_cook [label=\"Cooking Method\\n(boil, saute, simmer)\", shape=box, fillcolor=lightsalmon, style=filled, fontsize=10];",
        "        legend_combine [label=\"Combination\\n(combine, mix)\", shape=box, fillcolor=lightcyan, style=filled, fontsize=10];",
        "        legend_separate [label=\"Separation\\n(strain)\", shape=box, fillcolor=lightgray, style=filled, fontsize=10];",
        "        ",
        "        legend_input -> legend_intermediate -> legend_output -> legend_equipment [style=invis];",
        "        legend_prep -> legend_cook -> legend_combine -> legend_separate [style=invis];",
        "        ",
        "    }",
        "}"
    ])
    
    # Write file
    with open(output_file, 'w') as f:
        f.write('\n'.join(dot_content))
    
    print(f"DOT file generated: {output_file}")
    print("Visualization commands:")
    print(f"  dot -Tpng {output_file} -o Recipe\ DAG\ Example.png")
    print(f"  dot -Tsvg {output_file} -o Recipe\ DAG\ Example.svg")

def main():
    """Main demonstration of a recipe DAG."""
    print("Recipe DAG Demonstration")
    print("===========================================")
    
    recipe, symbols, items = build_recipe_dag()
    
    all_connected = validate_all_connections(recipe, symbols, items)
    print(f"\n=== CONNECTION STATUS ===")
    print(f"All nodes properly connected: {all_connected}")
    
    if not all_connected:
        print("ERROR: Some nodes are disconnected!")
        return
    
    analyze_dag(recipe, symbols, items)
    generate_dot_file(recipe)
    
    print(f"\n=== Recipe Summary ===")
    print(f"Recipe: {recipe.title}")
    
    base_ingredients = [i for i in recipe.item_nodes if i.is_input_operand() and hasattr(i, 'ingredient_id')]
    equipment_items = [i for i in recipe.item_nodes if hasattr(i, 'equipment_id')]
    intermediate_ingredients = [i for i in recipe.item_nodes if i.is_intermediate_operand() and hasattr(i, 'ingredient_id')]
    final_ingredients = [i for i in recipe.item_nodes if i.is_output_operand() and hasattr(i, 'ingredient_id')]
    
    print(f"- {len(base_ingredients)} base ingredients")
    print(f"- {len(equipment_items)} pieces of equipment")
    print(f"- {len(intermediate_ingredients)} intermediate ingredients")
    print(f"- {len(final_ingredients)} final ingredients")
    print(f"- {len(recipe.action_nodes)} distinct operations")

if __name__ == "__main__":
    main()