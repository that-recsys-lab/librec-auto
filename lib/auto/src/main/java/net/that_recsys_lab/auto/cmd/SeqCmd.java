package net.that_recsys_lab.auto.cmd;

import net.that_recsys_lab.auto.IJobCmd;
import net.that_recsys_lab.auto.AutoRecommenderJob;
import net.librec.common.LibrecException;

import java.io.IOException;
import java.util.List;

public class SeqCmd implements IJobCmd {
    private AutoRecommenderJob job;
    private List<IJobCmd> m_cmds;
    // C'tor
    public SeqCmd(AutoRecommenderJob job, List<IJobCmd> cmds) {
        this.job = job;
        this.m_cmds = cmds;
    }


    public void execute() throws LibrecException, IOException, ClassNotFoundException {
        for (IJobCmd cmd : m_cmds) {
            cmd.execute();
        }
    }
}
