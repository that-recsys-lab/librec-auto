package net.that_recsys_lab.auto.cmd;

import net.that_recsys_lab.auto.AutoRecommenderJob;
import net.that_recsys_lab.auto.IJobCmd;
import net.librec.common.LibrecException;
import net.librec.conf.Configuration;
import net.librec.recommender.Recommender;
import net.librec.recommender.RecommenderContext;
import net.librec.util.ReflectionUtil;

import java.io.IOException;

public class ReRunEvalCmd implements IJobCmd {
    private AutoRecommenderJob job;
    private int m_splitId;

    private String ORACLE_ALGO_CLASSNAME = "net.that_recsys_lab.auto.OracleAlgo";

    // C'tor
    public ReRunEvalCmd(AutoRecommenderJob job) {
        this.job = job;
        this.m_splitId = 1;
    }
    public ReRunEvalCmd(AutoRecommenderJob job, int splitId){
        this.job = job;
        this.m_splitId = splitId;
    }
    public void execute() throws LibrecException, IOException, ClassNotFoundException {
        executeEval();
    }
    /**
     * ~ Auto-Method ~
     * Executes Recommender Job with OracleALgo on a single test-train set.
     *
     * Assumes result data exists
     *
     * @throws ClassNotFoundException
     * @throws IOException
     * @throws LibrecException
     */
    public void executeEval() throws LibrecException, IOException, ClassNotFoundException { // TODO error handling
        //getConf().set("data.model.splitter", "testset"); redundant
        getConf().set("rec.recommender.class", ORACLE_ALGO_CLASSNAME); // Todo change this to dynamic name/not hardcoded
        //job.getData() = ReflectionUtil.newInstance((Class<DataModel>) job.getDataModelClass(), getConf());
        Integer dataDir = getConf().get("dfs.data.dir").length() + 1;
        int endingIndex = trainFileNameGen().length() - 10;
        getConf().set("data.splitter.cv.index", String.valueOf(this.m_splitId));
        getConf().set("data.input.path", trainFileNameGen().substring(dataDir, endingIndex));
        getConf().set("data.testset.path", testFileNameGen().substring(dataDir));
        job.getData().buildDataModel();
        recalculateMetrics();
    }

    /**
     * ~ Auto-Method ~
     * Changes: Doesn't save out file
     *
     * Aux function to load results and OracleAlgo
     *
     * @throws ClassNotFoundException
     * @throws IOException
     * @throws LibrecException
     */
    private void recalculateMetrics() throws LibrecException, IOException, ClassNotFoundException {
        RecommenderContext context = new RecommenderContext(getConf(), job.getData());
        job.generateSimilarityAutoOverload(context);
        Recommender recommender = (Recommender) ReflectionUtil.newInstance((Class<Recommender>) job.getRecommenderClass(), getConf());
        recommender.recommend(context);
        job.executeEvaluatorAutoOverload(recommender);
    }

    /**                              ~  Auto Aux functions  ~
     * Helper functions:
     *
     * getConf()                          -> Retrieves properties file from invoker.
     * trainFileNameGen()/testFileNameGen -> Facade for fileNameGenAux() for ease and readability of use.
     * fileNameGenAux()                   -> Creates file name string based on train/test and split (defaults to 1 if not cv.)
     *
     */
    private Configuration getConf() {
        return job.getConf();
    }
    private String trainFileNameGen() throws IOException, ClassNotFoundException { return fileNameGenAux(true); }
    private String testFileNameGen() throws IOException, ClassNotFoundException { return fileNameGenAux(false); }

    // Generate files paths
    private String fileNameGenAux(Boolean flag) throws IOException, ClassNotFoundException {
        String outputPath = getConf().get("dfs.data.dir")+'/'+getConf().get("dfs.split.dir");
        //Had to move "Split" dir into "Data" dir in order to maintain how LibRec searches for Data in directory...
        if (flag) {
            outputPath = outputPath+"/cv_"+ String.valueOf(this.m_splitId)+"/train.txt";
        }
        else {
            outputPath = outputPath+"/cv_"+String.valueOf(this.m_splitId)+"/test.txt";
        }
        return outputPath;
    }

}
