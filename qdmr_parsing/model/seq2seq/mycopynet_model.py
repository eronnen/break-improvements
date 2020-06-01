from model.seq2seq.seq2seq_model import Seq2seqModel
from evaluation.decomposition import Decomposition, get_decomposition_from_tokens
from utils.qdmr_identifier import mycopynet_qdmr_to_regular_qdmr


class MycopynetModel(Seq2seqModel):
    def _get_decompositions_from_predictions(self, preds):
        decompositions = []
        for pred in preds:
            if self.beam:
                pred_text = pred["predicted_tokens"][0]
            else:
                pred_text = pred["predicted_tokens"]

            qdmr_text = mycopynet_qdmr_to_regular_qdmr(' '.join(pred_text))
            qdmr_text_list = qdmr_text.split(' ')
            decompositions.append(get_decomposition_from_tokens(qdmr_text_list))

        return decompositions
