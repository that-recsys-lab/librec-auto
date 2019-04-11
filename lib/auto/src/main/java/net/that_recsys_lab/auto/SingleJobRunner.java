package net.that_recsys_lab.auto;

import net.librec.conf.Configuration;
import net.librec.job.RecommenderJob;

import java.io.FileInputStream;
import java.util.Properties;

/**
 * Adapted from net.librec.tool.driver.Driver.java
 * Created by Himan on 12/5/2016.
 */
// @DePaul-WIL
public class SingleJobRunner {

    public static void main(String[] args) throws Exception {
        Configuration conf = new Configuration();
        String confFilePath = args[0];

        Properties prop = new Properties();
        prop.load(new FileInputStream(confFilePath));
        for (String name : prop.stringPropertyNames()) {
            conf.set(name, prop.getProperty(name));
        }
        RecommenderJob job = new AutoRecommenderJob(conf);
        ((AutoRecommenderJob) job).setCommands(args[1]);
        job.runJob();
    }
}
