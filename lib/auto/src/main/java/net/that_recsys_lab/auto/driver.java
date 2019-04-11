package net.that_recsys_lab.auto;
//package net.librec.job;

import net.librec.job.RecommenderJob;
//import AutoRecommenderJob;

import net.librec.conf.Configuration;
import net.librec.math.algorithm.Randoms;
import java.io.FileInputStream;
import java.util.Properties;

public class driver {

    public static void main (String[] args){
        try{
            Configuration conf = new Configuration();
            String confFilePath = "lib/auto/test_eval/conf/conf2.properties";
            Properties prop = new Properties();
            prop.load(new FileInputStream(confFilePath));
            for (String name : prop.stringPropertyNames()) {
                conf.set(name, prop.getProperty(name));
            }
            Randoms.seed(201701);

            /*
            RecommenderJob job = new AutoRecommenderJob(conf);
            ((AutoRecommenderJob) job).setCommands("full");
            */
            RecommenderJob job = new RecommenderJob(conf);
            job.runJob();
        }
        catch(Exception e){
            e.printStackTrace();
        }
    }
}
