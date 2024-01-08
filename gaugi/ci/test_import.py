# Example CI script

def test_import():
    print ("Import test...", end='')
    try:
        import Gaugi
        from Gaugi import Algorithm
        print (" success!")
    except Exception as e:
        print (" failed :(")
        raise e
