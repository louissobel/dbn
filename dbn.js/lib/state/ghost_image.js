// 
// class DBNGhosts:
//     """
//     immutable state object representing ghosts
//     """
//     
//     def __init__(self):
//         self._ghost_hash = {}
//     
//     def __copy__(self):
//         new = DBNGhosts()
//         new._ghost_hash = copy.copy(self._ghost_hash)
//         return new
//     
//     def _make_key(self, line_no, arg_no):
//         return "l%da%d" % (line_no, arg_no)
//     
//     def _get_image(self, line_no, arg_no):
//         key = self._make_key(line_no, arg_no)
//         return self._ghost_hash.get(key)
// 
//     def _set_image(self, line_no, arg_no, dbnimage):
//         key = self._make_key(line_no, arg_no)
//         self._ghost_hash[key] = dbnimage
//         return dbnimage
//         
//     def _add_points(self, line_no, arg_no, points):
//         """
//         points is a list of tuples
//         """
//         image = self._get_image(line_no, arg_no)
//         if image is None:
//             image = DBNImage(color=0, mode='1')  # bitmap mode
//             
//         new_image = image.set_pixels((x, y, 1) for x,y in points)
//         self._set_image(line_no, arg_no, new_image)
//     
//     @Producer
//     def add_points(old, new, line_no, arg_no, points):
//         new._add_points(line_no, arg_no, points)
//     
//     @Producer
//     def add_point(old, new, line_no, arg_no, point):
//         """
//         point is an (x, y) tuple
//         """
//         new._add_points(line_no, arg_no, [point])
//     
//     @Producer
//     def add_dimension_line(old, new, line_no, arg_no, direction, x, y):
//         """
//         adds a dimension line!
//         """
//         points = utils.dimension_line(direction, x, y)
//         new._add_points(line_no, arg_no, points)
//  
//     @Producer
//     def add_points_to_callstack(old, new, walking_env, arg_no, points):
//         while walking_env.parent is not None:
//             line_no = walking_env.base_line_no
//             if line_no == -1:
//                 raise AssertionError("base_line_no of an environment should not be -1 unless it is the root environment")
//             new._add_points(line_no, arg_no, points)
//             walking_env = walking_env.parent
//             
//     @Producer
//     def add_point_to_callstack(old, new, walking_env, arg_no, point):
//         while walking_env.parent is not None:
//             line_no = walking_env.base_line_no
//             if line_no == -1:
//                 raise AssertionError("base_line_no of an environment should not be -1 unless it is the root environment")
//             new._add_points(line_no, arg_no, [point])
//             walking_env = walking_env.parent