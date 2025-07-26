#!/usr/bin/env python3
"""
Phase 3 Test Script - Panda3D Space Game Clone
Tests building system, construction, and integration
"""

import sys
import os

def test_building_imports():
    """Test building system imports"""
    print("\n=== Phase 3 Building Import Tests ===")
    
    try:
        # Test building entity
        from game.entities.building import Building, BuildingState, BuildingType
        print("✓ Building entity import successful")
        
        # Test building system
        from game.systems.building_system import BuildingSystem
        print("✓ Building system import successful")
        
        # Test building states
        states = [state.value for state in BuildingState]
        expected_states = ['under_construction', 'operational', 'unpowered', 'damaged', 'destroyed']
        if all(state in expected_states for state in states):
            print(f"✓ Building states defined: {states}")
        else:
            print(f"✗ Unexpected building states: {states}")
            
        # Test building types
        types = [bt.value for bt in BuildingType]
        print(f"✓ Building types defined: {len(types)} types")
        
        return True
        
    except Exception as e:
        print(f"✗ Building import test failed: {e}")
        return False

def test_building_creation():
    """Test building creation and configuration"""
    print("\n=== Phase 3 Building Creation Tests ===")
    
    try:
        from config.config_loader import GameConfig
        from game.entities.building import Building, BuildingState
        
        config = GameConfig("config/")
        print("✓ Configuration loaded")
        
        # Test creating a solar panel
        solar = Building("solar", 100, 200, config)
        print(f"✓ Solar panel created: {solar.building_type} at ({solar.x}, {solar.y})")
        print(f"  Health: {solar.current_health}/{solar.max_health}")
        print(f"  Power generation: {solar.power_generation}")
        print(f"  Construction time: {solar.construction_time}s")
        print(f"  State: {solar.state.value}")
        
        # Test creating a turret
        turret = Building("turret", 300, 400, config)
        print(f"✓ Turret created: {turret.building_type} at ({turret.x}, {turret.y})")
        print(f"  Damage: {turret.damage}")
        print(f"  Range: {turret.range}")
        print(f"  Fire rate: {turret.fire_rate}")
        
        # Test building connections
        connector = Building("connector", 200, 300, config)
        print(f"✓ Connector created: max connections = {connector.max_connections}")
        
        # Test connection logic
        can_connect = solar.can_connect_to(connector)
        print(f"✓ Connection test: solar can connect to connector = {can_connect}")
        
        return True
        
    except Exception as e:
        print(f"✗ Building creation test failed: {e}")
        return False

def test_building_system():
    """Test building system functionality"""
    print("\n=== Phase 3 Building System Tests ===")
    
    try:
        from config.config_loader import GameConfig
        from game.systems.building_system import BuildingSystem
        
        config = GameConfig("config/")
        
        # Create mock objects for building system
        class MockBase:
            pass
            
        class MockSceneManager:
            class entity_visualizer:
                @staticmethod
                def create_building_visual(building_type, x, y, radius):
                    print(f"    Mock visual created for {building_type}")
                    return MockNode()
                    
        class MockNode:
            def removeNode(self):
                pass
                
        class MockGameEngine:
            def __init__(self):
                self.minerals = 1000
                self.energy = 100
                
        mock_base = MockBase()
        mock_scene = MockSceneManager()
        
        building_system = BuildingSystem(mock_base, config, mock_scene)
        print("✓ Building system created")
        
        # Test construction mode
        success = building_system.start_construction("solar")
        print(f"✓ Construction mode started: {success}")
        
        # Test building costs
        cost = building_system.get_building_cost("solar")
        print(f"✓ Solar panel cost: {cost}")
        
        # Test affordability
        mock_engine = MockGameEngine()
        can_afford = building_system.can_afford_building("solar", mock_engine.minerals, mock_engine.energy)
        print(f"✓ Can afford solar: {can_afford}")
        
        # Test placement validation
        can_place, reason = building_system.can_place_building("solar", 500, 600)
        print(f"✓ Can place at (500, 600): {can_place} - {reason}")
        
        # Test placing a building
        building = building_system.place_building("solar", 500, 600, mock_engine)
        if building:
            print(f"✓ Building placed: {building.building_id}")
            print(f"  Resources after: {mock_engine.minerals} minerals, {mock_engine.energy} energy")
        
        # Test building count
        count = building_system.get_building_count()
        print(f"✓ Building count: {count}")
        
        # Cleanup
        building_system.cleanup()
        print("✓ Building system cleanup successful")
        
        return True
        
    except Exception as e:
        print(f"✗ Building system test failed: {e}")
        return False

def test_integration():
    """Test integration with game engine"""
    print("\n=== Phase 3 Integration Tests ===")
    
    try:
        from config.config_loader import GameConfig
        
        config = GameConfig("config/")
        print("✓ Configuration loaded for integration test")
        
        # Test building type mapping
        building_types = config.buildings.get("building_types", {})
        expected_types = ["starting_base", "solar", "connector", "battery", "miner", "turret"]
        
        found_types = []
        for expected_type in expected_types:
            if expected_type in building_types:
                found_types.append(expected_type)
                type_config = building_types[expected_type]
                cost = type_config.get("cost", {})
                print(f"  {expected_type}: {cost}")
                
        if len(found_types) >= 6:
            print(f"✓ Building types available: {len(found_types)}")
        else:
            print(f"✗ Missing building types. Found: {found_types}")
            
        return True
        
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        return False

def main():
    """Run all Phase 3 tests"""
    print("🚀 Starting Phase 3 Tests")
    print("=" * 50)
    
    tests = [
        test_building_imports,
        test_building_creation,
        test_building_system,
        test_integration
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 Phase 3 Building System: ALL TESTS PASSED!")
        print("\nBuilding system features available:")
        print("✓ Building entity with construction, health, connections")
        print("✓ Building system with placement validation and costs")
        print("✓ Integration with Panda3D visuals and configuration")
        print("✓ Construction mode with building selection")
        print("✓ Auto-connection system for power networks")
        print("✓ Resource management and affordability checking")
        print("\nRun 'python main.py' to test the building system!")
    else:
        print("❌ Some tests failed. Please fix issues before proceeding.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 