import numpy as np
import pytest
from CAMASim.function.writeNoise import writeNoise


class TestWriteNoiseBitflip:
    
    def get_base_config(self, variation_config):
        """Helper method to create a complete writeNoise config"""
        return {
            "hasWriteNoise": True,
            "device": "Numerical", 
            "noiseType": ["variation"],
            "cellDesign": "dummy",  # Required by writeNoise.__init__
            "minConductance": 0.0,  # Required for RRAM device type
            "maxConductance": 1.0,  # Required for RRAM device type
            "variation": variation_config
        }
    
    def test_bitflip_zero_probability(self):
        """Test that no bits flip when probability is 0"""
        variation_config = {
            "type": "bitflip",
            "value": 0.0
        }
        config = self.get_base_config(variation_config)
        
        noise_gen = writeNoise(config)
        original_array = np.array([[1, 1, 1], [0, 1, 0], [1, 0, 1]])
        result = noise_gen.add_write_noise(original_array.copy())
        
        np.testing.assert_array_equal(result, original_array)
    
    def test_bitflip_full_probability(self):
        """Test that all 1s flip when probability is 1.0"""
        variation_config = {
            "type": "bitflip",
            "value": 1.0
        }
        config = self.get_base_config(variation_config)
        
        noise_gen = writeNoise(config)
        original_array = np.array([[1, 1, 1], [0, 1, 0], [1, 0, 1]])
        expected = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
        result = noise_gen.add_write_noise(original_array.copy())
        
        np.testing.assert_array_equal(result, expected)
    
    def test_bitflip_only_affects_ones(self):
        """Test that only 1s can flip to 0s, 0s remain unchanged"""
        np.random.seed(42)  # For reproducible results
        
        variation_config = {
            "type": "bitflip",
            "value": 0.5
        }
        config = self.get_base_config(variation_config)
        
        noise_gen = writeNoise(config)
        original_array = np.array([[0, 0, 0], [0, 0, 0]])
        result = noise_gen.add_write_noise(original_array.copy())
        
        # All zeros should remain zeros
        np.testing.assert_array_equal(result, original_array)
    
    def test_bitflip_statistical_behavior(self):
        """Test that bitflip probability is approximately correct over many trials"""
        np.random.seed(None)  # Use random seed
        flip_prob = 0.3
        
        variation_config = {
            "type": "bitflip",
            "value": flip_prob
        }
        config = self.get_base_config(variation_config)
        
        noise_gen = writeNoise(config)
        
        # Create array of all 1s (2D array as required by writeNoise)
        array_size = 10000
        ones_array = np.ones((array_size, 1))
        
        # Run multiple trials
        num_trials = 100
        flip_rates = []
        
        for _ in range(num_trials):
            result = noise_gen.add_write_noise(ones_array.copy())
            flips = np.sum(ones_array - result)  # Count how many 1s became 0s
            flip_rate = flips / array_size
            flip_rates.append(flip_rate)
        
        mean_flip_rate = np.mean(flip_rates)
        
        # Check that observed flip rate is close to expected (within 5%)
        assert abs(mean_flip_rate - flip_prob) < 0.05, f"Expected ~{flip_prob}, got {mean_flip_rate}"
    
    def test_bitflip_different_array_shapes(self):
        """Test bitflip works with different array shapes"""
        variation_config = {
            "type": "bitflip",
            "value": 1.0
        }
        config = self.get_base_config(variation_config)
        
        noise_gen = writeNoise(config)
        
        # Test 2D array (minimum required shape)
        array_2d_simple = np.array([[1, 1, 1]])
        result_2d_simple = noise_gen.add_write_noise(array_2d_simple.copy())
        np.testing.assert_array_equal(result_2d_simple, np.zeros((1, 3)))
        
        # Test 2D array  
        array_2d = np.array([[1, 1], [1, 1]])
        result_2d = noise_gen.add_write_noise(array_2d.copy())
        np.testing.assert_array_equal(result_2d, np.zeros((2, 2)))
        
        # Test 3D array with shape (x, y, 2)
        array_3d = np.ones((2, 2, 2))
        result_3d = noise_gen.add_write_noise(array_3d.copy())
        np.testing.assert_array_equal(result_3d, np.zeros((2, 2, 2)))
    
    def test_bitflip_missing_config_value(self):
        """Test that missing variation.value raises KeyError"""
        variation_config = {
            "type": "bitflip"
            # Missing "value" key
        }
        config = self.get_base_config(variation_config)
        
        noise_gen = writeNoise(config)
        test_array = np.array([[1, 0, 1]])
        
        with pytest.raises(KeyError, match="Configuration missing 'variation.value'"):
            noise_gen.add_write_noise(test_array)
    
    def test_no_noise_when_disabled(self):
        """Test that no noise is applied when hasWriteNoise is False"""
        variation_config = {
            "type": "bitflip",
            "value": 1.0
        }
        config = self.get_base_config(variation_config)
        config["hasWriteNoise"] = False  # Disable noise
        
        noise_gen = writeNoise(config)
        original_array = np.array([[1, 1, 1], [0, 1, 0]])
        result = noise_gen.add_write_noise(original_array.copy())
        
        np.testing.assert_array_equal(result, original_array)