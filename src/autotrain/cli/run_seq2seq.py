from argparse import ArgumentParser

from autotrain import logger
from autotrain.cli.utils import get_field_info, seq2seq_munge_data
from autotrain.project import AutoTrainProject
from autotrain.trainers.seq2seq.params import Seq2SeqParams

from . import BaseAutoTrainCommand


def run_seq2seq_command_factory(args):
    return RunAutoTrainSeq2SeqCommand(args)


class RunAutoTrainSeq2SeqCommand(BaseAutoTrainCommand):
    @staticmethod
    def register_subcommand(parser: ArgumentParser):
        arg_list = get_field_info(Seq2SeqParams)
        arg_list = [
            {
                "arg": "--train",
                "help": "Command to train the model",
                "required": False,
                "action": "store_true",
            },
            {
                "arg": "--deploy",
                "help": "Command to deploy the model (limited availability)",
                "required": False,
                "action": "store_true",
            },
            {
                "arg": "--inference",
                "help": "Command to run inference (limited availability)",
                "required": False,
                "action": "store_true",
            },
        ] + arg_list
        run_seq2seq_parser = parser.add_parser("seq2seq", description="✨ Run AutoTrain Seq2Seq")
        for arg in arg_list:
            if "action" in arg:
                run_seq2seq_parser.add_argument(
                    arg["arg"],
                    help=arg["help"],
                    required=arg.get("required", False),
                    action=arg.get("action"),
                    default=arg.get("default"),
                )
            else:
                run_seq2seq_parser.add_argument(
                    arg["arg"],
                    help=arg["help"],
                    required=arg.get("required", False),
                    type=arg.get("type"),
                    default=arg.get("default"),
                    choices=arg.get("choices"),
                )
        run_seq2seq_parser.set_defaults(func=run_seq2seq_command_factory)

    def __init__(self, args):
        self.args = args

        store_true_arg_names = ["train", "deploy", "inference", "auto_find_batch_size", "push_to_hub", "peft"]
        for arg_name in store_true_arg_names:
            if getattr(self.args, arg_name) is None:
                setattr(self.args, arg_name, False)

        if self.args.train:
            if self.args.project_name is None:
                raise ValueError("Project name must be specified")
            if self.args.data_path is None:
                raise ValueError("Data path must be specified")
            if self.args.model is None:
                raise ValueError("Model must be specified")
            if self.args.push_to_hub:
                if self.args.username is None:
                    raise ValueError("Username must be specified for push to hub")
        else:
            raise ValueError("Must specify --train, --deploy or --inference")

    def run(self):
        logger.info("Running Seq2Seq Classification")
        if self.args.train:
            params = Seq2SeqParams(**vars(self.args))
            params = seq2seq_munge_data(params, local=self.args.backend.startswith("local"))
            project = AutoTrainProject(params=params, backend=self.args.backend)
            job_id = project.create()
            logger.info(f"Job ID: {job_id}")
