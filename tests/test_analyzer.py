import os
import unittest
import tempfile
from app import create_app, db
from app.models.user import User
from app.models.resume import Resume
from app.models.readiness import PlacementReadiness
from app.resume.parser import parse_resume

class AnalyzerTestCase(unittest.TestCase):
    def setUp(self):
        """Set up testing app and clean database before each test."""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create a default test user
        self.user = User(name="Tester", email="test@example.com")
        self.user.set_password("password")
        db.session.add(self.user)
        db.session.commit()
        
        self.user_id = self.user.id

    def tearDown(self):
        """Clean database and tear down context after each test."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_weighted_readiness_recalculation(self):
        """Test that the composite readiness score combines parts correctly (40/30/30)."""
        readiness = PlacementReadiness(
            user_id=self.user_id,
            resume_score=80.0,      # 80 * 0.40 = 32 points
            aptitude_score=70.0,    # 70 * 0.30 = 21 points
            interview_score=90.0    # 90 * 0.30 = 27 points
        )
        db.session.add(readiness)
        db.session.commit()
        
        readiness.calculate_overall()
        
        # Expected composite overall = 32 + 21 + 27 = 80.0
        self.assertEqual(readiness.overall_score, 80.0)
        self.assertEqual(readiness.readiness_status, 'Ready')
        
        # Test Almost Ready status
        readiness.resume_score = 50.0  # 50 * 0.40 = 20
        readiness.aptitude_score = 50.0 # 50 * 0.30 = 15
        readiness.interview_score = 50.0 # 50 * 0.30 = 15
        readiness.calculate_overall()   # Total = 50.0
        self.assertEqual(readiness.overall_score, 50.0)
        self.assertEqual(readiness.readiness_status, 'Almost Ready')

        # Test Needs Improvement status
        readiness.resume_score = 20.0
        readiness.aptitude_score = 20.0
        readiness.interview_score = 20.0
        readiness.calculate_overall()
        self.assertEqual(readiness.overall_score, 20.0)
        self.assertEqual(readiness.readiness_status, 'Needs Improvement')

    def test_resume_parsing_skill_detector(self):
        """Test resume parser skill detection from a raw text string context."""
        # Create a mock PDF with text and write it temporarily
        mock_pdf_text = (
            b"%PDF-1.4\n"
            b"1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj\n"
            b"2 0 obj <</Type /Pages /Kids [3 0 R] /Count 1>> endobj\n"
            b"3 0 obj <</Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources <</Font <</F1 5 0 R>>>>>> endobj\n"
            b"4 0 obj <</Length 70>> stream\n"
            b"BT /F1 12 Tf 70 700 Td (Python Docker Jenkins Git AWS C++) Tj ET\n"
            b"endstream\n"
            b"endobj\n"
            b"5 0 obj <</Type /Font /Subtype /Type1 /BaseFont /Helvetica>> endobj\n"
            b"xref\n"
            b"0 6\n"
            b"0000000000 65535 f\n"
            b"0000000009 00000 n\n"
            b"0000000056 00000 n\n"
            b"0000000111 00000 n\n"
            b"0000000224 00000 n\n"
            b"0000000344 00000 n\n"
            b"trailer <</Size 6 /Root 1 0 R>>\n"
            b"startxref\n"
            b"421\n"
            b"%%EOF\n"
        )
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf:
            temp_pdf.write(mock_pdf_text)
            temp_path = temp_pdf.name
            
        try:
            score, detected, missing = parse_resume(temp_path, self.app.config['NLTK_DATA_DIR'])
            
            # Python(6) + Docker(6) + Jenkins(6) + Git(6) + AWS(7) + C++(6) = 37 points
            self.assertEqual(score, 37.0)
            self.assertIn('Python', detected)
            self.assertIn('Docker', detected)
            self.assertIn('Jenkins', detected)
            self.assertIn('Git', detected)
            self.assertIn('AWS', detected)
            self.assertIn('C++', detected)
            self.assertNotIn('Java', detected)
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)

if __name__ == '__main__':
    unittest.main()
