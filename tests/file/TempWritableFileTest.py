import unittest
import gc

from os.path import exists

from walletflow.dags.lazyutils.file.TempWritableFile import TempWritableFile


class TempWritableFileTest(unittest.TestCase):
    def create_temp_file(self) -> str:
        tmp_file = TempWritableFile(file_prefix='unittest_', mode='w')
        file_path = tmp_file.file_path

        with tmp_file as tmp:
            self.assertTrue(exists(file_path))

            with open(file_path, 'w') as f:
                i = f.write('testing')

                self.assertEqual(7, i, "Problem when writing to temp file")

        del tmp_file

        return file_path

    def test_writablefile(self):
        file_path = self.create_temp_file()
        gc.collect()

        self.assertFalse(exists(file_path), "File still created")
