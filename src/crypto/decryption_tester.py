import os
import binascii
from typing import Dict, List, Tuple, Optional
from .decryption import PupDecryption
from ..utils.logging import PupLogger

class DecryptionTester:
    def __init__(self):
        self.decryption = PupDecryption()
        self.logger = PupLogger()
        
    def test_file(self, file_path: str) -> Dict:
        """Test the decryption of a PUP file"""
        results = {
            'file': os.path.basename(file_path),
            'analysis': None,
            'decryption_attempts': [],
            'success': False,
            'key': None,
            'iv': None
        }
        
        try:
            # Read the file
            with open(file_path, 'rb') as f:
                data = f.read()
                
            # Analyze the file
            results['analysis'] = self.decryption.analyze_file(data)
            
            # If encryption is suspected, try to decrypt
            if results['analysis']['encryption']['suspected']:
                self.logger.info(f"Attempting decryption for {file_path}")
                
                # Try suspected keys
                for key_info in results['analysis']['suspected_keys']:
                    if key_info['confidence'] > 0.7:
                        key = bytes.fromhex(key_info['key'])
                        for i in range(16):
                            iv = bytes([i] * 16)
                            success, decrypted = self.decryption.try_decrypt(data[:32], key, iv)
                            
                            results['decryption_attempts'].append({
                                'key': key_info['key'],
                                'iv': binascii.hexlify(iv).decode(),
                                'success': success
                            })
                            
                            if success:
                                results['success'] = True
                                results['key'] = key_info['key']
                                results['iv'] = binascii.hexlify(iv).decode()
                                break
                                
                        if results['success']:
                            break
                            
            return results
            
        except Exception as e:
            self.logger.error(f"Error during test of {file_path}: {str(e)}")
            results['error'] = str(e)
            return results
            
    def test_directory(self, directory: str) -> List[Dict]:
        """Test the decryption of all PUP files in a directory"""
        results = []
        
        for file_name in os.listdir(directory):
            if file_name.endswith('.pup'):
                file_path = os.path.join(directory, file_name)
                result = self.test_file(file_path)
                results.append(result)
                
        return results
        
    def generate_report(self, results: List[Dict]) -> str:
        """Generate a report of the test results"""
        report = []
        report.append("=== PUP Decryption Report ===")
        report.append(f"Total files tested: {len(results)}")
        
        success_count = sum(1 for r in results if r.get('success', False))
        report.append(f"Files decrypted successfully: {success_count}")
        
        for result in results:
            report.append("\n---")
            report.append(f"File: {result['file']}")
            
            if 'error' in result:
                report.append(f"Error: {result['error']}")
                continue
                
            if result['analysis']['encryption']['suspected']:
                report.append("Suspected encryption: Yes")
                report.append(f"Detected patterns: {', '.join(result['analysis']['encryption']['patterns'])}")
                
                if result['success']:
                    report.append("Decryption successful!")
                    report.append(f"Key: {result['key']}")
                    report.append(f"IV: {result['iv']}")
                else:
                    report.append("Decryption failed")
                    report.append(f"Attempts: {len(result['decryption_attempts'])}")
            else:
                report.append("Suspected encryption: No")
                
        return "\n".join(report) 