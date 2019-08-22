import unittest
from base import DBSession,engine,Base
from models import Sample,Analysis,Variant,AnalysisVariant,Panel,Gene,GenePanel,Transcript,SamplePanel
from extract import *


class TestCalculateGeminiAF(unittest.TestCase):

    def test_get_variant_id(self):
        id = 4810052
        self.assertEqual(get_variant_id(1,16271260,'G','A'),id)

    def test_find_samples_with_variant(self):
        """Tests  that given a variant id, function returns the correct variant attributes
        """
        result = find_samples_with_variant(11736653)[0]
        expected = ['cardiac',1052,12941.8,0.48384,1]
        self.assertEqual(result.name,'cardiac')
        self.assertEqual(result.depth, 1052)
        self.assertEqual(result.quality, 12941.8)
        self.assertEqual(result.allele_count, 1)
        self.assertEqual(result.AAF,0.48384)

    def test_calculate_frequency(self):
        """Tests that the correct frequency is calculated"""
        query_results = find_samples_with_variant(11736653)
        frequency = FrequencyOutput(3, 38532534,'C','T' , query_results,10079)
        self.assertEqual(frequency.calculate_frequency(),4.9608096041273936e-05)
        self.assertNotEqual(frequency.calculate_frequency(),5)



class TestGetPanelGenes(unittest.TestCase):

    def test_get_all_genes(self):

        with self.assertRaises(SystemExit):
            get_all_genes('NotAGene')

    def test_get_all_panels(self):
        with self.assertRaises(SystemExit):
            get_all_panels('NotAPanel')

    def test_get_panel_id(self):
        self.assertEqual(get_panel_id('CAKUT'),433)

    def test_get_gene_id(self):
        self.assertEqual(get_gene_id('PTEN'),9503)

    def test_get_genes(self):
        """tests correct list of genes is returned"""
        panel_id = 324
        genes = get_genes(panel_id)
        self.assertIn('BSND',genes.values())
        self.assertIn(211,genes.keys())

    def test_get_samples(self):
        """tests whether script extracts the correct samples"""
        panel_name = 'Aortopathy'
        samples = get_samples(panel_name)
        self.assertIn('G001657',samples)
        self.assertIn('X005562',samples)
        self.assertIsInstance(samples,list)

    def test_get_panels(self):

        gene_id =  19060
        panels = get_panels(gene_id)
        self.assertIsInstance(panels,list)
        self.assertIn('Primary Immunodeficiency (PID)',panels)


if __name__ == '__main__':
    unittest.main()
