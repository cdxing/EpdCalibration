# EPD Calibration tools for EPDers

1.Getting The Source Code
--------------------------
- Open a terminal and get the source code:
```
git clone https://github.com/cdxing/EpdCalibration.git
```

2.Check status
--------------------------
- You can check the status use
```
git status
```
Now you will see you are On branch master.

3.Create New Branch
--------------------------
- If you want to have your own version of codes, you can create a new branch. (You can merge branches later)
- To create and switch to a new branch:
```
git checkout -b example
```
- Then check status again:
```
git status
```
- You are now On branch example, if you want to go back to master branch, you do:
```
git checkout master
```
- To view both remote and local branches:
```
git branch -a
```
4.Edit, add and commit your files
--------------------------
Feel free to modify or add new files.

5.Commit Changes
--------------------------
- If you want to publish your branch to the GitHub, you can do:
```
git add *
git commit -m "some init commit"
git push
```
- GitHub will ask for you Username and passwords

6.Updating The Package
--------------------------
If you want to get the latest version of codes from GitHub:
```
git pull
```
7.Git: “please tell me who you are” error
I use Atom editor to connect with GitHub. There's a link in the reference if you are interested in using Atom. This is an error that I came across when I use Atom editor to do the initial commit, the solution is:
```
git init
git config user.name "someone"
git config user.email "someone@someplace.com"
```
8.References
- How to connect Github with Atom - Easiest Way! https://www.youtube.com/watch?time_continue=403&v=6HsZMl-qV5k&feature=emb_logo
- Basic Branching and Merging https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging
- git-please-tell-me-who-you-are-error https://stackoverflow.com/questions/11656761/git-please-tell-me-who-you-are-error
