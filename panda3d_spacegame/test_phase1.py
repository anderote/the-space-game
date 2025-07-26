#!/usr/bin/env python3
"""
Test script for Phase 1 - Verify setup without opening graphics window
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all imports work correctly"""
    print("=== Phase 1 Import Tests ===")
    
    try:
        from config.config_loader import GameConfig
        print("✓ Configuration system import successful")
    except Exception as e:
        print(f"✗ Configuration import failed: {e}")
        return False
    
    try:
        from game.core.engine import Panda3DGameEngine
        print("✓ Game engine import successful")
    except Exception as e:
        print(f"✗ Game engine import failed: {e}")
        return False
    
    try:
        from game.panda3d.camera_controller import Panda3DCamera
        print("✓ Camera controller import successful")
    except Exception as e:
        print(f"✗ Camera controller import failed: {e}")
        return False
    
    try:
        from game.panda3d.scene_manager import SceneManager
        print("✓ Scene manager import successful")
    except Exception as e:
        print(f"✗ Scene manager import failed: {e}")
        return False
    
    try:
        from game.panda3d.input_system import Panda3DInputSystem
        print("✓ Input system import successful")
    except Exception as e:
        print(f"✗ Input system import failed: {e}")
        return False
    
    return True

def test_configuration():
    """Test configuration loading"""
    print("\n=== Configuration Tests ===")
    
    try:
        from config.config_loader import GameConfig
        config = GameConfig("config/")
        print("✓ Configuration loaded successfully")
        
        # Test key configuration sections
        display_config = config.game.get('display', {})
        print(f"✓ Display config: {display_config.get('screen_width', 1600)}x{display_config.get('screen_height', 900)}")
        
        camera_config = config.game.get('camera', {})
        print(f"✓ Camera config: zoom {camera_config.get('zoom_min', 0.5)}-{camera_config.get('zoom_max', 5.0)}")
        
        building_types = list(config.buildings.get("building_types", {}).keys())
        print(f"✓ Building config: {len(building_types)} building types")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def test_panda3d_basic():
    """Test basic Panda3D functionality"""
    print("\n=== Panda3D Basic Tests ===")
    
    try:
        from direct.showbase.ShowBase import ShowBase
        from panda3d.core import OrthographicLens, AmbientLight
        print("✓ Panda3D core imports successful")
        
        # Test lens creation without ShowBase
        lens = OrthographicLens()
        lens.setFilmSize(1600, 900)
        print("✓ Orthographic lens creation successful")
        
        # Test light creation
        light = AmbientLight('test')
        light.setColor((1, 1, 1, 1))
        print("✓ Light creation successful")
        
        return True
        
    except Exception as e:
        print(f"✗ Panda3D basic test failed: {e}")
        return False

def test_file_structure():
    """Test that all required files exist"""
    print("\n=== File Structure Tests ===")
    
    required_files = [
        "main.py",
        "config/config_loader.py",
        "config/game_config.json",
        "config/buildings.json",
        "config/enemies.json",
        "config/waves.json",
        "config/research.json",
        "config/controls.json",
        "game/__init__.py",
        "game/core/__init__.py",
        "game/core/engine.py",
        "game/panda3d/__init__.py",
        "game/panda3d/camera_controller.py",
        "game/panda3d/scene_manager.py",
        "game/panda3d/input_system.py",
        "game/systems/__init__.py",
        "game/entities/__init__.py",
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"✓ {file_path}")
    
    if missing_files:
        print(f"✗ Missing files: {missing_files}")
        return False
    else:
        print("✓ All required files present")
        return True

def main():
    """Run all Phase 1 tests"""
    print("🚀 Starting Phase 1 Tests")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Run all tests
    all_tests_passed &= test_file_structure()
    all_tests_passed &= test_imports()
    all_tests_passed &= test_configuration()
    all_tests_passed &= test_panda3d_basic()
    
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("🎉 Phase 1 Setup: ALL TESTS PASSED!")
        print("\nPhase 1 is ready! You can now:")
        print("1. Run 'python main.py' to start the Panda3D application")
        print("2. Use ESC to quit, SPACE to start game, P to pause")
        print("3. Proceed to Phase 2 implementation")
        return 0
    else:
        print("❌ Phase 1 Setup: SOME TESTS FAILED")
        print("Please fix the issues above before proceeding.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 