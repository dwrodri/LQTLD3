# Linear Quadtrees with Level Differences in Python 3 (LQTLD3)


This is the Python 3 version of [LQTLD](https://github.com/dwrodri/LQTLD), and is a much cleaner implementation. This (and the original Python 2 implementation) are based on [A Constant-Time Algorithm for Finding Neighbors in Quadtrees (2009)](http://ieeexplore.ieee.org/document/4538229/) by Kunio Aizawa and Shojiro Tanaka.

# Motivation

I wrote the original Python 2 implementation of this paper so that I can efficiently perform some path planning operations on a Raspberry Pi for a robotics project. By converting the occupancy grid to a linear quadtree, I reduced the the search space by >90%.

This data structure has two major strengths:
* It can represent a 2-d matrix of bits efficiently, especially if the values of one category are grouped together.
* You can get the neighbors of any cell in the quadtree in constant time.

Quadtrees are popular for programming video game NPCS because they're a good way to store spacial data for path planning algorithms.

While I have yet to see an example of this in the wild, I think quadtrees could serve as a way for processing Karnaugh maps. In order to make a powerful K-map parser, I'd have to extend the logic to support input data that has more than two dimensions.

# Long-term Plans

Unless the Internet tells me otherwise, I'm going to stop working on the original LQTLD and put my free time towards this implementation instead. I'd like to see if I can rewrite this a third time in a language more suited to this sort of work so that I can efficiently parallelize `divide()` and `assign_color()` methods. Then I could build wrappers for other languages for people to use this.

As previously mentioned, it would be nice to extend the functionality of the algorithm to support n-dimensional arrays, not just 2-d arrays. I think Shrack's Algorithm, and the adjustments proposed by Aizawa support this. A working version of constant-time neighbor cell search in 3-dimensional space could be useful for computer vision projects, or time series forecasting.
# To-Do
- [ ] Add PyPI support
- [ ] Extend to support Karnaugh map operation for up to four variables. 
- [ ] Find some way of speeding up cell division
- [x] Speed up matrix ops with [numpy](http://numpy.org)
