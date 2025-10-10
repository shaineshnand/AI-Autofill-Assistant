#!/usr/bin/env python
"""
Universal Document Processor with Machine Learning Capabilities
This system can learn and adapt to any document type through training
"""
import os
import sys
import json
import pickle
import numpy as np
import cv2
import fitz  # PyMuPDF
import pytesseract
from typing import List, Dict, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DocumentField:
    """Enhanced field representation with learning capabilities"""
    id: str
    field_type: str
    x_position: int
    y_position: int
    width: int
    height: int
    page_number: int
    context: str = ""
    confidence: float = 0.0
    detection_method: str = ""
    document_type: str = ""
    field_label: str = ""
    expected_format: str = ""
    validation_rules: List[str] = None
    
    def __post_init__(self):
        if self.validation_rules is None:
            self.validation_rules = []

@dataclass
class DocumentTemplate:
    """Template for a specific document type"""
    document_type: str
    description: str
    field_patterns: Dict[str, List[str]]
    layout_patterns: Dict[str, Any]
    validation_rules: Dict[str, List[str]]
    confidence_threshold: float = 0.7
    training_samples: List[Dict] = None
    
    def __post_init__(self):
        if self.training_samples is None:
            self.training_samples = []

class UniversalDocumentProcessor:
    """
    Universal document processor that can learn and adapt to any document type
    """
    
    def __init__(self, model_dir: str = "models"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        
        # Machine learning models
        self.field_type_classifier = None
        self.document_type_classifier = None
        self.text_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        
        # Document templates and patterns
        self.document_templates: Dict[str, DocumentTemplate] = {}
        self.field_patterns = {}
        self.layout_patterns = {}
        
        # Training data
        self.training_data = []
        self.validation_data = []
        
        # Load existing models and templates
        self._load_models()
        self._load_templates()
        
        # Initialize default patterns
        self._initialize_default_patterns()
    
    def _initialize_default_patterns(self):
        """Initialize default field and document patterns"""
        
        # Enhanced field patterns for various document types
        self.field_patterns = {
            'personal_info': {
                'name': [
                    'name', 'full name', 'first name', 'last name', 'given name', 
                    'surname', 'family name', 'applicant name', 'patient name',
                    'student name', 'employee name', 'client name'
                ],
                'email': [
                    'email', 'e-mail', 'email address', 'electronic mail',
                    'contact email', 'primary email', 'work email'
                ],
                'phone': [
                    'phone', 'telephone', 'mobile', 'cell phone', 'home phone',
                    'work phone', 'contact number', 'phone number'
                ],
                'address': [
                    'address', 'home address', 'mailing address', 'street address',
                    'residential address', 'billing address', 'shipping address'
                ],
                'date_of_birth': [
                    'date of birth', 'dob', 'birth date', 'birthday', 'date born',
                    'age', 'born', 'birth'
                ],
                'ssn': [
                    'ssn', 'social security number', 'social security',
                    'ss number', 'tax id', 'tax identification'
                ],
                'id_number': [
                    'id number', 'identification number', 'license number',
                    'passport number', 'driver license', 'employee id'
                ]
            },
            'financial': {
                'income': [
                    'income', 'annual income', 'monthly income', 'salary',
                    'wages', 'gross income', 'net income', 'total income'
                ],
                'bank_account': [
                    'bank account', 'account number', 'routing number',
                    'checking account', 'savings account', 'account info'
                ],
                'credit_score': [
                    'credit score', 'fico score', 'credit rating', 'credit history'
                ],
                'assets': [
                    'assets', 'total assets', 'net worth', 'property value',
                    'investment value', 'savings', 'retirement funds'
                ]
            },
            'medical': {
                'patient_id': [
                    'patient id', 'patient number', 'medical record number',
                    'mrn', 'patient identifier'
                ],
                'insurance': [
                    'insurance', 'health insurance', 'insurance provider',
                    'policy number', 'group number', 'member id'
                ],
                'medications': [
                    'medications', 'current medications', 'prescription drugs',
                    'drugs', 'medicines', 'pharmaceuticals'
                ],
                'allergies': [
                    'allergies', 'allergic to', 'drug allergies', 'food allergies',
                    'known allergies', 'allergy information'
                ]
            },
            'legal': {
                'case_number': [
                    'case number', 'case id', 'docket number', 'file number',
                    'reference number', 'claim number'
                ],
                'court': [
                    'court', 'court name', 'jurisdiction', 'venue',
                    'filing court', 'hearing court'
                ],
                'attorney': [
                    'attorney', 'lawyer', 'counsel', 'legal representative',
                    'advocate', 'barrister'
                ]
            },
            'education': {
                'student_id': [
                    'student id', 'student number', 'enrollment number',
                    'registration number', 'student identifier'
                ],
                'gpa': [
                    'gpa', 'grade point average', 'cumulative gpa',
                    'overall gpa', 'academic average'
                ],
                'major': [
                    'major', 'field of study', 'program', 'degree program',
                    'academic program', 'concentration'
                ]
            }
        }
        
        # Document type patterns
        self.document_type_patterns = {
            'application_form': [
                'application', 'apply', 'applicant', 'submission', 'enrollment',
                'registration', 'admission', 'membership'
            ],
            'contract': [
                'contract', 'agreement', 'terms', 'conditions', 'clause',
                'signature', 'party', 'obligation'
            ],
            'invoice': [
                'invoice', 'bill', 'payment', 'amount due', 'total',
                'subtotal', 'tax', 'invoice number'
            ],
            'medical_form': [
                'medical', 'health', 'patient', 'doctor', 'physician',
                'diagnosis', 'treatment', 'symptoms'
            ],
            'legal_document': [
                'legal', 'court', 'law', 'attorney', 'plaintiff',
                'defendant', 'judgment', 'settlement'
            ],
            'financial_form': [
                'financial', 'income', 'expenses', 'assets', 'liabilities',
                'credit', 'loan', 'mortgage'
            ]
        }
    
    def _load_models(self):
        """Load pre-trained models if they exist"""
        try:
            model_path = self.model_dir / "field_type_classifier.pkl"
            if model_path.exists():
                self.field_type_classifier = joblib.load(model_path)
                logger.info("Loaded field type classifier")
            
            model_path = self.model_dir / "document_type_classifier.pkl"
            if model_path.exists():
                self.document_type_classifier = joblib.load(model_path)
                logger.info("Loaded document type classifier")
            
            # Load vectorizer if it exists
            vectorizer_path = self.model_dir / "text_vectorizer.pkl"
            if vectorizer_path.exists():
                self.text_vectorizer = joblib.load(vectorizer_path)
                logger.info("Loaded text vectorizer")
                
        except Exception as e:
            logger.warning(f"Could not load models: {e}")
    
    def _save_models(self):
        """Save trained models"""
        try:
            if self.field_type_classifier:
                joblib.dump(self.field_type_classifier, self.model_dir / "field_type_classifier.pkl")
            
            if self.document_type_classifier:
                joblib.dump(self.document_type_classifier, self.model_dir / "document_type_classifier.pkl")
            
            if self.text_vectorizer:
                joblib.dump(self.text_vectorizer, self.model_dir / "text_vectorizer.pkl")
                
            logger.info("Models saved successfully")
        except Exception as e:
            logger.error(f"Error saving models: {e}")
    
    def _load_templates(self):
        """Load document templates"""
        try:
            templates_path = self.model_dir / "document_templates.json"
            if templates_path.exists():
                with open(templates_path, 'r') as f:
                    templates_data = json.load(f)
                    for template_data in templates_data:
                        template = DocumentTemplate(**template_data)
                        self.document_templates[template.document_type] = template
                logger.info(f"Loaded {len(self.document_templates)} document templates")
        except Exception as e:
            logger.warning(f"Could not load templates: {e}")
    
    def _save_templates(self):
        """Save document templates"""
        try:
            templates_path = self.model_dir / "document_templates.json"
            templates_data = [asdict(template) for template in self.document_templates.values()]
            with open(templates_path, 'w') as f:
                json.dump(templates_data, f, indent=2)
            logger.info("Templates saved successfully")
        except Exception as e:
            logger.error(f"Error saving templates: {e}")
    
    def classify_document_type(self, text: str, layout_features: Dict = None) -> Tuple[str, float]:
        """
        Classify document type using machine learning
        """
        if not self.document_type_classifier:
            # Fallback to pattern matching
            return self._classify_document_type_pattern(text)
        
        try:
            # Extract features
            text_features = self.text_vectorizer.transform([text])
            
            # Predict document type
            prediction = self.document_type_classifier.predict(text_features)[0]
            confidence = self.document_type_classifier.predict_proba(text_features).max()
            
            return prediction, confidence
        except Exception as e:
            logger.error(f"Error classifying document type: {e}")
            return self._classify_document_type_pattern(text)
    
    def _classify_document_type_pattern(self, text: str) -> Tuple[str, float]:
        """Fallback document type classification using patterns"""
        text_lower = text.lower()
        
        scores = {}
        for doc_type, patterns in self.document_type_patterns.items():
            score = sum(1 for pattern in patterns if pattern in text_lower)
            scores[doc_type] = score
        
        if scores:
            best_type = max(scores, key=scores.get)
            confidence = min(0.9, scores[best_type] / len(self.document_type_patterns[best_type]))
            return best_type, confidence
        
        return "unknown", 0.0
    
    def detect_fields_universal(self, file_path: str) -> List[DocumentField]:
        """
        Universal field detection that works for any document type
        """
        try:
            # Determine document type
            text = self._extract_text(file_path)
            doc_type, confidence = self.classify_document_type(text)
            
            logger.info(f"Detected document type: {doc_type} (confidence: {confidence:.2f})")
            
            # Get document template if available
            template = self.document_templates.get(doc_type)
            
            # Detect fields using multiple methods
            fields = []
            
            # Method 1: AcroForm fields (native PDF forms)
            fields.extend(self._detect_acroform_fields(file_path))
            
            # Method 2: Visual field detection
            fields.extend(self._detect_visual_fields(file_path))
            
            # Method 3: Text pattern detection
            fields.extend(self._detect_text_pattern_fields(text, doc_type))
            
            # Method 4: Layout-based detection
            fields.extend(self._detect_layout_fields(file_path))
            
            # Method 5: Machine learning-based detection
            if self.field_type_classifier:
                fields.extend(self._detect_ml_fields(file_path, text))
            
            # Enhance fields with template information
            if template:
                fields = self._enhance_fields_with_template(fields, template)
            
            # Remove duplicates and merge similar fields
            fields = self._merge_similar_fields(fields)
            
            # Assign document type to all fields
            for field in fields:
                field.document_type = doc_type
            
            logger.info(f"Detected {len(fields)} fields")
            return fields
            
        except Exception as e:
            logger.error(f"Error in universal field detection: {e}")
            return []
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text from document"""
        try:
            if file_path.lower().endswith('.pdf'):
                doc = fitz.open(file_path)
                text = ""
                for page in doc:
                    text += page.get_text() + "\n"
                doc.close()
                return text
            else:
                # For other file types, use OCR
                image = cv2.imread(file_path)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                return pytesseract.image_to_string(gray)
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return ""
    
    def _detect_acroform_fields(self, file_path: str) -> List[DocumentField]:
        """Detect native PDF form fields"""
        fields = []
        try:
            if file_path.lower().endswith('.pdf'):
                doc = fitz.open(file_path)
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    widgets = list(page.widgets())
                    
                    for widget in widgets:
                        field = DocumentField(
                            id=f"acroform_{widget.field_name}",
                            field_type=self._classify_pdf_field_type(widget),
                            x_position=int(widget.rect.x0),
                            y_position=int(widget.rect.y0),
                            width=int(widget.rect.width),
                            height=int(widget.rect.height),
                            page_number=page_num,
                            context=widget.field_name or "",
                            confidence=0.95,
                            detection_method="acroform"
                        )
                        fields.append(field)
                doc.close()
        except Exception as e:
            logger.error(f"Error detecting AcroForm fields: {e}")
        
        return fields
    
    def _detect_visual_fields(self, file_path: str) -> List[DocumentField]:
        """Detect fields using visual analysis"""
        fields = []
        try:
            # Convert PDF to images
            images = self._pdf_to_images(file_path)
            
            for page_num, image in images:
                # Detect rectangular fields
                fields.extend(self._detect_rectangular_fields(image, page_num))
                
                # Detect underline fields
                fields.extend(self._detect_underline_fields(image, page_num))
                
                # Detect checkbox fields
                fields.extend(self._detect_checkbox_fields(image, page_num))
        
        except Exception as e:
            logger.error(f"Error in visual field detection: {e}")
        
        return fields
    
    def _pdf_to_images(self, pdf_path: str) -> List[Tuple[int, np.ndarray]]:
        """Convert PDF pages to images"""
        images = []
        try:
            doc = fitz.open(pdf_path)
            for page_num in range(len(doc)):
                page = doc[page_num]
                mat = fitz.Matrix(2.0, 2.0)  # 2x scale
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                
                # Convert to OpenCV image
                nparr = np.frombuffer(img_data, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                images.append((page_num, image))
            
            doc.close()
        except Exception as e:
            logger.error(f"Error converting PDF to images: {e}")
        
        return images
    
    def _detect_rectangular_fields(self, image: np.ndarray, page_num: int) -> List[DocumentField]:
        """Detect rectangular form fields"""
        fields = []
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Multiple thresholding approaches
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for i, contour in enumerate(contours):
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter by size and aspect ratio
                if 50 <= w <= 400 and 15 <= h <= 50:
                    # Check if area is blank
                    roi = gray[y:y+h, x:x+w]
                    if roi.size > 0:
                        mean_intensity = np.mean(roi)
                        std_intensity = np.std(roi)
                        dark_pixels = np.sum(roi < 100)
                        dark_ratio = dark_pixels / roi.size
                        
                        if mean_intensity > 200 and std_intensity < 40 and dark_ratio < 0.1:
                            field = DocumentField(
                                id=f"rect_p{page_num}_{i}",
                                field_type="text",
                                x_position=x,
                                y_position=y,
                                width=w,
                                height=h,
                                page_number=page_num,
                                context="rectangular field",
                                confidence=0.8,
                                detection_method="visual_rectangular"
                            )
                            fields.append(field)
        
        except Exception as e:
            logger.error(f"Error detecting rectangular fields: {e}")
        
        return fields
    
    def _detect_underline_fields(self, image: np.ndarray, page_num: int) -> List[DocumentField]:
        """Detect fields with underlines"""
        fields = []
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect horizontal lines
            edges = cv2.Canny(gray, 50, 150)
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=100, maxLineGap=10)
            
            if lines is not None:
                for i, line in enumerate(lines):
                    x1, y1, x2, y2 = line[0]
                    
                    # Check if it's a horizontal line
                    if abs(y2 - y1) < 5:
                        # Look for text above the line
                        text_region = gray[max(0, y1-50):y1, x1:x2]
                        if text_region.size > 0:
                            text = pytesseract.image_to_string(text_region, config='--psm 8').strip()
                            
                            if text and len(text) > 2:
                                field_type = self._classify_field_type_from_text(text)
                                
                                field = DocumentField(
                                    id=f"underline_p{page_num}_{i}",
                                    field_type=field_type,
                                    x_position=x1,
                                    y_position=y1-30,
                                    width=x2-x1,
                                    height=30,
                                    page_number=page_num,
                                    context=text.lower(),
                                    confidence=0.9,
                                    detection_method="visual_underline"
                                )
                                fields.append(field)
        
        except Exception as e:
            logger.error(f"Error detecting underline fields: {e}")
        
        return fields
    
    def _detect_checkbox_fields(self, image: np.ndarray, page_num: int) -> List[DocumentField]:
        """Detect checkbox fields"""
        fields = []
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect small square shapes
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for i, contour in enumerate(contours):
                x, y, w, h = cv2.boundingRect(contour)
                
                # Check if it's roughly square and small
                if 10 <= w <= 30 and 10 <= h <= 30 and abs(w - h) < 5:
                    # Look for text near the checkbox
                    text_region = gray[y:y+h, x+w:x+w+200]
                    if text_region.size > 0:
                        text = pytesseract.image_to_string(text_region, config='--psm 8').strip()
                        
                        if text:
                            field = DocumentField(
                                id=f"checkbox_p{page_num}_{i}",
                                field_type="checkbox",
                                x_position=x,
                                y_position=y,
                                width=w,
                                height=h,
                                page_number=page_num,
                                context=text.lower(),
                                confidence=0.9,
                                detection_method="visual_checkbox"
                            )
                            fields.append(field)
        
        except Exception as e:
            logger.error(f"Error detecting checkbox fields: {e}")
        
        return fields
    
    def _detect_text_pattern_fields(self, text: str, doc_type: str) -> List[DocumentField]:
        """Detect fields based on text patterns"""
        fields = []
        try:
            lines = text.split('\n')
            
            for line_num, line in enumerate(lines):
                line_lower = line.lower().strip()
                
                # Check against field patterns
                for field_type, patterns in self.field_patterns.get('personal_info', {}).items():
                    for pattern in patterns:
                        if pattern in line_lower:
                            # Estimate field position (this is simplified)
                            field = DocumentField(
                                id=f"text_pattern_{line_num}",
                                field_type=field_type,
                                x_position=200,  # Estimated position
                                y_position=line_num * 25,  # Estimated position
                                width=200,
                                height=25,
                                page_number=0,
                                context=line_lower,
                                confidence=0.7,
                                detection_method="text_pattern"
                            )
                            fields.append(field)
                            break
        
        except Exception as e:
            logger.error(f"Error detecting text pattern fields: {e}")
        
        return fields
    
    def _detect_layout_fields(self, file_path: str) -> List[DocumentField]:
        """Detect fields based on document layout analysis"""
        fields = []
        # Implementation for layout-based field detection
        # This would analyze document structure, tables, forms, etc.
        return fields
    
    def _detect_ml_fields(self, file_path: str, text: str) -> List[DocumentField]:
        """Detect fields using machine learning models"""
        fields = []
        # Implementation for ML-based field detection
        # This would use trained models to identify fields
        return fields
    
    def _classify_pdf_field_type(self, widget) -> str:
        """Classify PDF widget type"""
        try:
            if hasattr(widget, 'field_type'):
                field_type_map = {
                    1: 'text',
                    2: 'checkbox',
                    3: 'radio',
                    4: 'dropdown',
                    5: 'signature'
                }
                return field_type_map.get(widget.field_type, 'text')
        except:
            pass
        return 'text'
    
    def _classify_field_type_from_text(self, text: str) -> str:
        """Classify field type from text label"""
        text_lower = text.lower()
        
        # Check against all field patterns
        for category, patterns in self.field_patterns.items():
            for field_type, pattern_list in patterns.items():
                for pattern in pattern_list:
                    if pattern in text_lower:
                        return field_type
        
        return 'text'
    
    def _enhance_fields_with_template(self, fields: List[DocumentField], template: DocumentTemplate) -> List[DocumentField]:
        """Enhance fields with template information"""
        for field in fields:
            # Add template-specific information
            if field.context in template.field_patterns:
                field.expected_format = template.field_patterns[field.context]
            
            # Add validation rules
            if field.field_type in template.validation_rules:
                field.validation_rules = template.validation_rules[field.field_type]
        
        return fields
    
    def _merge_similar_fields(self, fields: List[DocumentField]) -> List[DocumentField]:
        """Merge similar fields to avoid duplicates"""
        merged_fields = []
        
        for field in fields:
            # Check if similar field already exists
            similar = False
            for existing in merged_fields:
                if (abs(field.x_position - existing.x_position) < 20 and
                    abs(field.y_position - existing.y_position) < 20 and
                    field.page_number == existing.page_number):
                    similar = True
                    # Merge field information
                    if field.confidence > existing.confidence:
                        merged_fields.remove(existing)
                        merged_fields.append(field)
                    break
            
            if not similar:
                merged_fields.append(field)
        
        return merged_fields
    
    def train_model(self, training_data: List[Dict]) -> Dict[str, float]:
        """
        Train the machine learning models with new data
        """
        try:
            # Prepare training data
            X_text = []
            y_field_types = []
            y_doc_types = []
            
            for sample in training_data:
                X_text.append(sample.get('text', ''))
                y_field_types.append(sample.get('field_type', 'text'))
                y_doc_types.append(sample.get('document_type', 'unknown'))
            
            # Vectorize text
            X_vectorized = self.text_vectorizer.fit_transform(X_text)
            
            # Train field type classifier
            self.field_type_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
            self.field_type_classifier.fit(X_vectorized, y_field_types)
            
            # Train document type classifier
            self.document_type_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
            self.document_type_classifier.fit(X_vectorized, y_doc_types)
            
            # Evaluate models
            X_train, X_test, y_field_train, y_field_test = train_test_split(X_vectorized, y_field_types, test_size=0.2)
            X_train, X_test, y_doc_train, y_doc_test = train_test_split(X_vectorized, y_doc_types, test_size=0.2)
            
            field_score = self.field_type_classifier.score(X_test, y_field_test)
            doc_score = self.document_type_classifier.score(X_test, y_doc_test)
            
            # Save models
            self._save_models()
            
            return {
                'field_type_accuracy': field_score,
                'document_type_accuracy': doc_score,
                'training_samples': len(training_data)
            }
            
        except Exception as e:
            logger.error(f"Error training models: {e}")
            return {'error': str(e)}
    
    def add_training_sample(self, document_path: str, field_annotations: List[Dict]):
        """
        Add a training sample to improve the model
        """
        try:
            text = self._extract_text(document_path)
            doc_type, _ = self.classify_document_type(text)
            
            for annotation in field_annotations:
                sample = {
                    'text': text,
                    'field_type': annotation.get('field_type', 'text'),
                    'document_type': doc_type,
                    'context': annotation.get('context', ''),
                    'confidence': annotation.get('confidence', 1.0)
                }
                self.training_data.append(sample)
            
            logger.info(f"Added {len(field_annotations)} training samples")
            
        except Exception as e:
            logger.error(f"Error adding training sample: {e}")
    
    def create_document_template(self, document_type: str, description: str, 
                               field_patterns: Dict, validation_rules: Dict) -> bool:
        """
        Create a new document template
        """
        try:
            template = DocumentTemplate(
                document_type=document_type,
                description=description,
                field_patterns=field_patterns,
                validation_rules=validation_rules,
                layout_patterns={}
            )
            
            self.document_templates[document_type] = template
            self._save_templates()
            
            logger.info(f"Created template for {document_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating template: {e}")
            return False
    
    def get_system_stats(self) -> Dict[str, Any]:
        """
        Get system statistics and performance metrics
        """
        return {
            'document_templates': len(self.document_templates),
            'training_samples': len(self.training_data),
            'field_patterns': sum(len(patterns) for patterns in self.field_patterns.values()),
            'models_loaded': {
                'field_type_classifier': self.field_type_classifier is not None,
                'document_type_classifier': self.document_type_classifier is not None
            }
        }

def convert_to_dict(fields: List[DocumentField]) -> List[Dict]:
    """Convert DocumentField objects to dictionaries"""
    return [asdict(field) for field in fields]

# Example usage and testing
if __name__ == "__main__":
    # Initialize the universal processor
    processor = UniversalDocumentProcessor()
    
    # Get system statistics
    stats = processor.get_system_stats()
    print("System Statistics:")
    print(json.dumps(stats, indent=2))
    
    # Example: Process a document
    # fields = processor.detect_fields_universal("sample_document.pdf")
    # print(f"Detected {len(fields)} fields")
    
    # Example: Add training data
    # training_data = [
    #     {'text': 'Please enter your name:', 'field_type': 'name', 'document_type': 'application_form'},
    #     {'text': 'Email address:', 'field_type': 'email', 'document_type': 'application_form'}
    # ]
    # results = processor.train_model(training_data)
    # print("Training results:", results)
