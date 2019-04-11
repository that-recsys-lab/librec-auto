package net.that_recsys_lab.auto.cmd;

import net.that_recsys_lab.auto.AutoRecommenderJob;
import net.that_recsys_lab.auto.IJobCmd;
import net.librec.common.LibrecException;
import net.librec.conf.Configuration;
import net.librec.recommender.Recommender;
import net.librec.recommender.RecommenderContext;
import net.librec.util.ReflectionUtil;

import java.io.IOException;

public class ExpCmd implements IJobCmd{
    private AutoRecommenderJob job;
    private int m_splitId;

    // C'tor
    public ExpCmd(AutoRecommenderJob job){
        this.job = job;
        this.m_splitId = 1;
    }

    public ExpCmd(AutoRecommenderJob job, int splitId){
        this.job = job;
        this.m_splitId = splitId;
    }

    /**
     * ~ Auto-Method ~
     * Executes Recommender Job on a single test-train set.
     *
     * Loads pre-split data
     *
     * @throws ClassNotFoundException
     * @throws IOException
     * @throws LibrecException
     */
    public void execute() throws IOException, ClassNotFoundException, LibrecException {
        job.getLOG().info("ExpCMD: START - Executing recommender job on "+String.valueOf(this.m_splitId+1)+".");
        getConf().set("data.model.splitter", "testset");
        Integer dataDir = getConf().get("dfs.data.dir").length()+1;  // used to remove the extra "data/" segment of the path...
        getConf().set("data.splitter.cv.index", String.valueOf(this.m_splitId));
        getConf().set("data.input.path", trainFileNameGen().substring(dataDir));
        getConf().set("data.testset.path", testFileNameGen().substring(dataDir));
        try {
            job.getData().buildDataModel();
        } catch (LibrecException e) {
            e.printStackTrace();
        }
        executeRecommenderJob();
        job.getLOG().info("ExpCMD: COMPLETE");
    }

    /**
     * ~ Edited LibRec Method ~
     * Changes: Removed first call to generateDataModel().  Auto execution will always generate model before this method is called
     *
     * execute Recommender Job
     *
     * @throws LibrecException
     *             If an LibrecException error occurs.
     * @throws ClassNotFoundException
     *             if can't find the class of filter
     * @throws IOException
     *             If an I/O error occurs.
     */

    private void executeRecommenderJob() throws ClassNotFoundException, LibrecException, IOException {
        RecommenderContext context = new RecommenderContext(getConf(), job.getData());
        job.generateSimilarityAutoOverload(context);
        Recommender recommender = (Recommender) ReflectionUtil.newInstance((Class<Recommender>) job.getRecommenderClass(), getConf());
        recommender.recommend(context);
        job.m_recommenders.add(this.m_splitId-1, recommender);
    }

    /**                              ~  Auto Aux functions  ~
     * Helper functions:
     *
     * getConf()                          -> Retrieves properties file from invoker.
     * trainFileNameGen()/testFileNameGen -> Facade for fileNameGenAux() for ease and readability of use.
     * fileNameGenAux()                   -> Creates file name string based on train/test and split (defaults to 1 if not cv.)
     *
     */

    private Configuration getConf() { return job.getConf(); }
    private String trainFileNameGen() throws IOException, ClassNotFoundException { return fileNameGenAux(true); }
    private String testFileNameGen() throws IOException, ClassNotFoundException { return fileNameGenAux(false); }

    // Generate files paths
    private String fileNameGenAux(Boolean flag) throws IOException, ClassNotFoundException {
        String outputPath = getConf().get("dfs.data.dir")+'/'+getConf().get("dfs.split.dir");
        //Had to move "Split" dir into "Data" dir in order to maintain how LibRec searches for Data in directory...
        if (flag) {
            outputPath = outputPath+"/cv_"+ this.m_splitId+"/train.txt";
        }
        else {
            outputPath = outputPath+"/cv_"+this.m_splitId+"/test.txt";
        }
        return outputPath;
    }
}