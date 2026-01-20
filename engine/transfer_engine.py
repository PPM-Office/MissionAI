import json
import logging
import time
import traceback
from typing import Dict, List, Optional
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mission_ai_debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MissionAIError(Exception):
    """Custom exception for Mission AI errors"""
    pass

class TransferEngine:
    def __init__(self):
        self.retry_count = 3
        self.retry_delay = 5
        logger.info("TransferEngine initialized")
    
    def safe_load_json_file(self, filepath: str) -> Optional[Dict]:
        """Safely load JSON file with error handling"""
        try:
            logger.info(f"Loading JSON file: {filepath}")
            with open(filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)
            logger.info(f"Successfully loaded {filepath}")
            return data
        except FileNotFoundError:
            logger.error(f"File not found: {filepath}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in {filepath}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error loading {filepath}: {str(e)}")
            logger.debug(traceback.format_exc())
            return None
    
    def safe_scrape_with_retry(self, scrape_function, *args, **kwargs) -> Optional[Dict]:
        """Execute scraping function with retry logic"""
        last_exception = None
        
        for attempt in range(self.retry_count):
            try:
                logger.info(f"Scraping attempt {attempt + 1}/{self.retry_count}")
                result = scrape_function(*args, **kwargs)
                
                if result is None:
                    raise MissionAIError("Scraper returned None")
                
                logger.info("Scraping successful")
                return result
                
            except Exception as e:
                last_exception = e
                logger.warning(f"Scraping attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < self.retry_count - 1:
                    logger.info(f"Waiting {self.retry_delay} seconds before retry...")
                    time.sleep(self.retry_delay)
                    
        logger.error(f"All scraping attempts failed. Last error: {str(last_exception)}")
        return None
    
    def handle_pendulum_error(self, error_message: str) -> bool:
        """Handle pendulum-related errors specifically"""
        pendulum_keywords = ['pendulum', 'loading', 'animation', 'spinner']
        if any(keyword in error_message.lower() for keyword in pendulum_keywords):
            logger.info("Detected pendulum/loading animation issue, attempting workaround...")
            time.sleep(10)  # Wait longer for animations to complete
            return True
        return False
    
    def validate_missionary_data(self, missionaries: List[Dict]) -> bool:
        """Validate missionary data structure"""
        if not missionaries:
            logger.warning("No missionary data found")
            return False
            
        required_fields = ['name', 'current_zone', 'current_area']
        valid_count = 0
        
        for i, missionary in enumerate(missionaries):
            try:
                # Check if it's a dict
                if not isinstance(missionary, dict):
                    logger.warning(f"Missionary {i} is not a dictionary")
                    continue
                
                # Check required fields
                missing_fields = [field for field in required_fields if field not in missionary]
                if missing_fields:
                    logger.warning(f"Missionary {i} missing fields: {missing_fields}")
                    continue
                
                valid_count += 1
                
            except Exception as e:
                logger.error(f"Error validating missionary {i}: {str(e)}")
                continue
        
        logger.info(f"Validated {valid_count}/{len(missionaries)} missionaries")
        return valid_count > 0
    
    def validate_car_data(self, cars: List[Dict]) -> bool:
        """Validate car data structure"""
        if not cars:
            logger.warning("No car data found")
            return True  # Cars might not be required
            
        valid_count = 0
        for i, car in enumerate(cars):
            try:
                if not isinstance(car, dict):
                    logger.warning(f"Car {i} is not a dictionary")
                    continue
                valid_count += 1
            except Exception as e:
                logger.error(f"Error validating car {i}: {str(e)}")
                continue
        
        logger.info(f"Validated {valid_count}/{len(cars)} cars")
        return True
    
    def compare_current_vs_desired(self, current_data: Dict, desired_data: Dict) -> Dict:
        """Compare current missionary locations vs desired assignments"""
        try:
            logger.info("Comparing current vs desired assignments")
            
            changes_needed = {
                'missionary_moves': [],
                'car_moves': [],
                'violations': []
            }
            
            # Compare missionary assignments
            current_missionaries = current_data.get('missionaries', [])
            desired_missionaries = desired_data.get('missionaries', [])
            
            # This is simplified - you'd need to match missionaries by ID/name
            # and compare their current vs desired locations
            
            logger.info("Comparison completed successfully")
            return changes_needed
            
        except Exception as e:
            logger.error(f"Error in comparison: {str(e)}")
            logger.debug(traceback.format_exc())
            return {'error': str(e)}
    
    def enforce_rules(self, travel_plan: Dict) -> Dict:
        """Enforce missionary travel rules"""
        try:
            logger.info("Enforcing travel rules")
            violations = []
            
            # Rule 1: Sisters/Elders separation
            # Rule 2: No solo travel  
            # Rule 3: 30-minute deviation limit
            # Rule 4: Companion separation handling
            
            # Add your rule enforcement logic here
            
            logger.info("Rule enforcement completed")
            return {'plan': travel_plan, 'violations': violations}
            
        except Exception as e:
            logger.error(f"Error enforcing rules: {str(e)}")
            logger.debug(traceback.format_exc())
            return {'error': str(e), 'violations': []}
    
    def generate_travel_plan(self, current_file: str = 'current_data.json', 
                           desired_file: str = 'desired_data.json') -> Optional[Dict]:
        """Main function to generate travel plan"""
        try:
            logger.info("Starting travel plan generation")
            
            # Load current data
            current_data = self.safe_load_json_file(current_file)
            if not current_data:
                raise MissionAIError(f"Failed to load current data from {current_file}")
            
            # Load desired data  
            desired_data = self.safe_load_json_file(desired_file)
            if not desired_data:
                raise MissionAIError(f"Failed to load desired data from {desired_file}")
            
            # Validate data
            if not self.validate_missionary_data(current_data.get('missionaries', [])):
                raise MissionAIError("Current missionary data validation failed")
                
            if not self.validate_missionary_data(desired_data.get('missionaries', [])):
                raise MissionAIError("Desired missionary data validation failed")
            
            # Compare current vs desired
            comparison_result = self.compare_current_vs_desired(current_data, desired_data)
            if 'error' in comparison_result:
                raise MissionAIError(f"Comparison failed: {comparison_result['error']}")
            
            # Enforce rules
            final_plan = self.enforce_rules(comparison_result)
            
            # Add timestamp
            final_plan['generated_at'] = datetime.now().isoformat()
            
            logger.info("Travel plan generation completed successfully")
            return final_plan
            
        except MissionAIError as e:
            logger.error(f"Mission AI Error: {str(e)}")
            return {'status': 'error', 'message': str(e)}
        except Exception as e:
            logger.error(f"Unexpected error in travel plan generation: {str(e)}")
            logger.debug(traceback.format_exc())
            return {'status': 'error', 'message': str(e), 'traceback': traceback.format_exc()}

# Example usage
def main():
    """Example of how to use the TransferEngine"""
    engine = TransferEngine()
    
    # Generate travel plan
    plan = engine.generate_travel_plan()
    
    if plan and plan.get('status') != 'error':
        print("Travel plan generated successfully!")
        # Save plan to file or update Google Sheet
    else:
        print("Error generating travel plan")
        print(plan.get('message', 'Unknown error'))

if __name__ == "__main__":
    main()
