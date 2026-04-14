If you get an error in your code, please describe your question in one message and attach MINIMUM CODE .

MINIMUM CODE is:

Code in which there are no unnecessary imports, classes, functions, widgets that are not related to the reproduction of the error.

KV string should be in the code, not in a separate file, for example:

[imports]

KV = """
    ...
"""

class Test(MDApp):
    def build(self):
        return Builder.load_string(KV)


Test().run()


If your code exceeds the allowed number of characters in one message, then this is not the MINIMUM CODE.


Your code should run in three clicks: Copy/Paste/Run
If this cannot be done without leaving Discord, this is not a MINIMUM CODE.

Before attaching the minimal code, describe how to interact with this code to reproduce the problem. Describe what this code does. Describe what this code does not do as you expect. Describe how you want this code to work.

Why are these requirements:

1. When you refactor your code in accordance with all of the above, you will find the error yourself 90% of the time.

2. You respect the developers who will look at your code. They don't need to look for an error and dig into large code if your code is 50-100 lines long.

3. No need to attach screenshots of the code. No need to attach screenshots of logs. Attach text only.