#!/usr/bin/env python
from nbt.nbt import _TAG_Numeric, MalformedFileError, NBTFile, TAGLIST
import sys,os,unittest
import tempfile, shutil
from io import BytesIO
from gzip import GzipFile

class BugfixTest(unittest.TestCase):
    """Bugfix regression tests."""
    def testEmptyFiles(self):
        """
        Opening an empty file causes an uncaught exception.
        https://github.com/twoolie/NBT/issues/issue/4
        """
        temp = BytesIO("")
        temp.seek(0)
        self.assertRaises(MalformedFileError, NBTFile, buffer=temp)

    def testProperlyClosed(self):
        """
        test that files opened from a file name are closed after 
        being written to. i.e. will read correctly in the future
        """
        # copy the file (don't work on the original test file)
        tempdir = tempfile.mkdtemp()
        filename = os.path.join(tempdir, 'bigtest.nbt')
        shutil.copy('bigtest.nbt', filename)
        
        #open the file
        f = NBTFile(filename)
        f.write_file()
        # make sure it can be read again directly after
        f = NBTFile(filename)
        
        # remove the temporary file
        try:
            shutil.rmtree(tempdir)
        except OSError as e:
            raise

class ReadWriteTest(unittest.TestCase):
    """test that we can read the test file correctly"""

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.filename = os.path.join(self.tempdir, 'bigtest.nbt')
        shutil.copy('bigtest.nbt', self.filename)

    def tearDown(self):
        try:
            shutil.rmtree(self.tempdir)
        except OSError as e:
            raise
    
    def testReadBig(self):
        mynbt = NBTFile(self.filename)
        self.assertTrue(mynbt.filename != None)
        self.assertEqual(len(mynbt.tags), 11)

    def testWriteBig(self):
        mynbt = NBTFile(self.filename)
        output = BytesIO()
        mynbt.write_file(buffer=output)
        self.assertEqual(GzipFile("bigtest.nbt").read(), output.getvalue())

    def testWriteback(self):
        mynbt = NBTFile(self.filename)
        mynbt.write_file()

class TreeManipulationTest(unittest.TestCase):

    def setUp(self):
        self.nbtfile = NBTFile()

    def testRootNodeSetup(self):
        self.nbtfile.name = "Hello World"
        self.assertEqual(self.nbtfile.name, "Hello World")

    def testTagNumeric(self):
        for tag in TAGLIST:
            if isinstance(TAGLIST[tag], _TAG_Numeric):
                tagobj = TAGLIST[tag](name="Test", value=10)
                self.assertEqual(byte.name, "Test", "Name not set correctly for %s" % TAGLIST[tag].__class__.__name__)
                self.assertEqual(byte.value, 10, "Value not set correctly for %s" % TAGLIST[tag].__class__.__name__)
                self.nbtfile.tags.append(tagobj)

    #etcetera..... will finish later

    def tearDown(self):
        del self.nbtfile

class EmptyStringTest(unittest.TestCase):

    def setUp(self):
        self.golden_value = "\x0A\0\x04Test\x08\0\x0Cempty string\0\0\0"
        self.nbtfile = NBTFile(buffer=BytesIO(self.golden_value))

    def testReadEmptyString(self):
        self.assertEqual(self.nbtfile.name, "Test")
        self.assertEqual(self.nbtfile["empty string"].value, "")

    def testWriteEmptyString(self):
        buffer = BytesIO()
        self.nbtfile.write_file(buffer=buffer)
        self.assertEqual(buffer.getvalue(), self.golden_value)

if __name__ == '__main__':
    unittest.main()
