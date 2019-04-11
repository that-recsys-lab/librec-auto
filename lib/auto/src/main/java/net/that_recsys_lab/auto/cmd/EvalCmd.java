package net.that_recsys_lab.auto.cmd;

import net.that_recsys_lab.auto.AutoRecommenderJob;
import net.that_recsys_lab.auto.IJobCmd;
import net.librec.common.LibrecException;
import net.librec.conf.Configuration;
import net.librec.filter.RecommendedFilter;
import net.librec.recommender.Recommender;
import net.librec.recommender.item.RecommendedItem;
import net.librec.util.FileUtil;
import net.librec.util.ReflectionUtil;

import java.io.IOException;
import java.util.List;

public class EvalCmd implements IJobCmd {
    private AutoRecommenderJob job;
    private int m_splitId;

    // C'tor
    public EvalCmd(AutoRecommenderJob job) {
        this.job = job;
        this.m_splitId = 1;
    }

    public EvalCmd(AutoRecommenderJob job, int splitId) {
        this.job = job;
        this.m_splitId = splitId;
    }

    public void execute() throws LibrecException, IOException, ClassNotFoundException {
        job.getLOG().info("EvalCMD: START");
        Recommender recommender = job.m_recommenders.get(this.m_splitId-1);
        job.executeEvaluatorAutoOverload(recommender);
        List<RecommendedItem> recommendedList = recommender.getRecommendedList(); // -> is this call necessary?
        recommendedList = filterResult(recommendedList); // -> is this call necessary?
        saveResult(recommendedList); // -> redundant to save results if using results already
        job.getLOG().info("EvalCMD: COMPLETE.");
    }

    /**
     * ~ Edited LibRec Method ~
     * Changes: Generates outpath with Aux function.  Save as .txt file. Commented block to catch outpath name existence.
     *
     * Save result.
     *
     * @param recommendedList         list of recommended items
     * @throws LibrecException        if error occurs
     * @throws IOException            if I/O error occurs
     * @throws ClassNotFoundException if class not found error occurs
     */

    public void saveResult(List<RecommendedItem> recommendedList) throws LibrecException, IOException, ClassNotFoundException {
        if (recommendedList != null && recommendedList.size() > 0) {
            String outputPath = getConf().get("dfs.result.dir");
            outputPath = outputPath + "/out-" + String.valueOf(getConf().getInt("data.splitter.cv.index", 1))+".txt";
            job.getLOG().info("Result path is " + outputPath);
            // Converting itemList to string
            StringBuilder sb = new StringBuilder();
            for (RecommendedItem recItem : recommendedList) {
                String userId = recItem.getUserId();
                String itemId = recItem.getItemId();
                String value = String.valueOf(recItem.getValue());
                sb.append(userId).append(",").append(itemId).append(",").append(value).append("\n");
            }
            String resultData = sb.toString();
            try {
                FileUtil.writeString(outputPath, resultData);
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }

    /**                              ~  Auto Aux functions  ~
     * Helper functions:
     *
     * getConf()                          -> Retrieves properties file from invoker.
     * filterResults()                    -> Filters the results.
     **/
    private Configuration getConf() {
        return job.getConf();
    }

    /**
     * Filter the results.
     * *This is a minorly edited LibRec private methods, initially located in RecommenderJob.java
     *
     * @param recommendedList  list of recommended items
     * @return recommended List
     * @throws ClassNotFoundException
     * @throws IOException
     */
    private List<RecommendedItem> filterResult(List<RecommendedItem> recommendedList) throws ClassNotFoundException, IOException {
        if (job.getFilterClass() != null) {
            RecommendedFilter filter = (RecommendedFilter) ReflectionUtil.newInstance(job.getFilterClass(), null);
            recommendedList = filter.filter(recommendedList);
        }
        return recommendedList;
    }
}