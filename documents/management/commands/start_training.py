"""
Django management command to start the training interface
"""
import os
import sys
import subprocess
import threading
import time
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Start the Universal Document Processing training interface'

    def add_arguments(self, parser):
        parser.add_argument(
            '--port',
            type=int,
            default=5001,
            help='Port for the training interface (default: 5001)'
        )
        parser.add_argument(
            '--host',
            type=str,
            default='0.0.0.0',
            help='Host for the training interface (default: 0.0.0.0)'
        )
        parser.add_argument(
            '--background',
            action='store_true',
            help='Run in background (non-blocking)'
        )

    def handle(self, *args, **options):
        port = options['port']
        host = options['host']
        background = options['background']
        
        self.stdout.write(
            self.style.SUCCESS('Starting Universal Document Processing Training Interface...')
        )
        
        # Check if ml_training_interface.py exists
        if not os.path.exists('ml_training_interface.py'):
            self.stdout.write(
                self.style.ERROR('Error: ml_training_interface.py not found in project root')
            )
            return
        
        # Initialize the training system
        try:
            from universal_document_processor import UniversalDocumentProcessor
            processor = UniversalDocumentProcessor()
            stats = processor.get_system_stats()
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ System initialized - Templates: {stats["document_templates"]}, '
                    f'Models: {stats["models_loaded"]}'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'⚠️ Warning: Could not initialize training system: {e}')
            )
        
        def start_training_server():
            """Start the training server"""
            try:
                # Modify the training interface to use the specified host and port
                cmd = [sys.executable, 'ml_training_interface.py']
                
                # Set environment variables for host and port
                env = os.environ.copy()
                env['TRAINING_HOST'] = host
                env['TRAINING_PORT'] = str(port)
                
                process = subprocess.Popen(
                    cmd,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Training interface started on http://{host}:{port}')
                )
                
                if not background:
                    # Wait for the process
                    process.wait()
                
                return process
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Error starting training interface: {e}')
                )
                return None
        
        if background:
            # Start in background
            thread = threading.Thread(target=start_training_server)
            thread.daemon = True
            thread.start()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Training interface starting in background on http://{host}:{port}'
                )
            )
            self.stdout.write(
                'Note: The training interface is running in the background. '
                'Use Ctrl+C to stop the Django server.'
            )
        else:
            # Start in foreground
            self.stdout.write(
                self.style.SUCCESS(
                    f'Starting training interface on http://{host}:{port}...'
                )
            )
            self.stdout.write(
                'Press Ctrl+C to stop both Django and training interface.'
            )
            
            try:
                start_training_server()
            except KeyboardInterrupt:
                self.stdout.write(
                    self.style.SUCCESS('\n✓ Training interface stopped')
                )

