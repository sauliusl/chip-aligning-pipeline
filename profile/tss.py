from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from profile.aligned_reads_mixin import AlignedReadsMixin
from profile.base import ProfileBase
from profile.peak_caller import MacsProfileMixin, FseqProfileMixin
from tss import BedTranscriptionStartSites


class ReadsPerTss(AlignedReadsMixin, ProfileBase):

    extend_5_to_3 = BedTranscriptionStartSites.extend_5_to_3
    extend_3_to_5 = BedTranscriptionStartSites.extend_3_to_5
    merge = BedTranscriptionStartSites.merge


    @property
    def areas_to_map_to_task(self):
        return BedTranscriptionStartSites(genome_version=self.genome_version,
                                          extend_5_to_3=self.extend_5_to_3,
                                          extend_3_to_5=self.extend_3_to_5,
                                          merge=self.merge)

    @property
    def parameters(self):
        super_parameters = super(ReadsPerTss, self).parameters
        features_parameters = self.features_to_map_task.parameters
        areas_to_map_parameters = self.areas_to_map_to_task.parameters

        return super_parameters + features_parameters + areas_to_map_parameters

class MacsPeaksPerTss(MacsProfileMixin, ReadsPerTss):

    @property
    def parameters(self):
        return super(MacsPeaksPerTss, self).parameters + self.additional_parameters()

class FseqPeaksPerTss(FseqProfileMixin, ReadsPerTss):
    pass

if __name__ == '__main__':
    import logging
    ReadsPerTss.logger().setLevel(logging.DEBUG)
    MacsPeaksPerTss.logger().setLevel(logging.DEBUG)
    ProfileBase.logger().setLevel(logging.DEBUG)
    logging.basicConfig()

    import luigi
    luigi.run()