try:
    from IPython import get_ipython
except:
    pass

from IPython.display import clear_output as cls

def colab_setup():
    ipython = get_ipython()
    script = """
            %pip install -q dagshub
            import dagshub.colab
            repo = dagshub.colab.login()

            !apt-get install tree -y
            !pip install scikit-learn
            !pip install progress        
            !pip install cvxpy
            cls()
            print("Dependencias instaladas!!")
            """

    ipython.run_cell(script)
