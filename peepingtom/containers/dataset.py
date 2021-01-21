from .datalist import DataList
from .datacrate import DataCrate
from ..depictors import DataSetDepictor
from ..analysis import classify_radial_profile, deduplicate_dataset
from ..utils import distinct_colors, faded_grey, wrapper_method


class DataSet(DataList):
    """
    A container for a collection of DataCrates
    """
    _valid_type = DataCrate
    _depictor_type = DataSetDepictor

    def show(self, *args, **kwargs):
        self.depictor.show(*args, **kwargs)

    def hide(self, *args, **kwargs):
        self.depictor.hide(*args, **kwargs)

    def read(self, paths, **kwargs):
        """
        read paths into datablocks and append them to the datacrates
        """
        from ..io_ import read
        self.extend(read(paths, **kwargs))

    def write(self, paths, **kwargs):
        """
        write datablock contents to disk
        """
        from ..io_ import write
        write(self, paths, **kwargs)

    @wrapper_method(classify_radial_profile, ignore_args=1)
    def classify_radial_profile(self, *args, **kwargs):
        # TODO: adapt to new depiction (plots are now handled by depictors!)
        centroids, _ = classify_radial_profile(self, *args, **kwargs)
        tag = kwargs.get('class_tag', 'class_radial')
        self.particles.flatten().depict(mode='class_plot', class_tag=tag)
        # colors = distinct_colors[:kwargs['n_classes']]
        # if kwargs['if_properties'] is not None:
            # colors.append(faded_grey)
        # for p in self.particles:
            # p.depictor.point_layer.face_color = kwargs['class_tag']
            # p.depictor.point_layer.face_color_cycle = [list(x) for x in colors]
        # if kwargs['if_properties'] is not None:
            # colors.pop()
        # class_names = [f'class{i}' for i in range(kwargs['n_classes'])]
        # self.add_plot(centroids, colors, class_names, f'{kwargs["class_tag"]}')

    @wrapper_method(deduplicate_dataset, ignore_args=1)
    def deduplicate(self, *args, **kwargs):
        return deduplicate_dataset(self, *args, **kwargs)

    def __and__(self, other):
        self._checktypes(other)
        out = self.__newlike__([])
        added = []
        for s_item in self:
            for o_item in other:
                if o_item.name == s_item.name:
                    out.append(s_item + o_item)
                    added.append(o_item)
                    break
            else:
                out.append(s_item)
        out.extend([item for item in other if item not in added])
        return out
